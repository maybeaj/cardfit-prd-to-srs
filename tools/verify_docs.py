#!/usr/bin/env python3
"""문서 정합성 검증기 — 산출물 간 ID·개수·참조가 어긋나지 않았는지 확인한다.

주장(문서에 적힌 수)과 실측(실제 세어본 수)이 다르면 실패로 본다.
"""
import re, sys, pathlib, json

D = pathlib.Path("docs")
SRS  = D / "[SRS 문서] CardFit (한글).md"
SDD  = D / "[설계 문서] CardFit (한글).md"
STD  = D / "[테스트 명세서] CardFit (한글).md"
GTD  = D / "[배포 게이트 데이터] CardFit (한글).md"
TASK = D / "[태스크 리스트] CardFit.md"

REQ = re.compile(r"REQ-(?:FUNC|NF|EXC)-\d{3}")
TC  = re.compile(r"TC-(?:FUNC|NF|EXC)-\d{3}")

def read(p): return p.read_text(encoding="utf-8")
def ids(t, pat): return set(pat.findall(t))

def section(t, start, end):
    try: return t[t.index(start): t.index(end)]
    except ValueError: return ""

fails, checks = [], []
def check(name, ok, detail=""):
    checks.append((name, ok, detail))
    if not ok: fails.append(name)

# ── 1. 파일 존재 ─────────────────────────────────────────
for p in (SRS, SDD, STD, GTD, TASK):
    check(f"파일 존재: {p.name}", p.exists())
if fails:
    for n, ok, d in checks: print(f"{'✅' if ok else '❌'} {n}")
    sys.exit(1)

srs, sdd, std, gtd, task = map(read, (SRS, SDD, STD, GTD, TASK))

# ── 2. 요구사항 ID 일관성 ────────────────────────────────
srs_req = ids(srs, REQ)
check("SRS 요구사항 27건", len(srs_req) == 27, f"실측 {len(srs_req)}건")

trace = section(srs, "## 5. 추적성 매트릭스", "## 6. 부록")
check("SRS 추적표 = 요구사항 전건", ids(trace, REQ) == srs_req,
      f"누락 {sorted(srs_req - ids(trace, REQ))}")

sdd_trace = section(sdd, "## 8. SRS ↔ 설계 추적", "## 9.")
check("SDD 추적표 = 요구사항 전건", ids(sdd_trace, REQ) == srs_req,
      f"누락 {sorted(srs_req - ids(sdd_trace, REQ))}")

std_trace = section(std, "## 5. 추적 매트릭스", "## 6.")
check("STD 추적표 = 요구사항 전건", ids(std_trace, REQ) == srs_req,
      f"누락 {sorted(srs_req - ids(std_trace, REQ))}")

# ── 3. 테스트 케이스 ─────────────────────────────────────
tc_body = set(re.findall(r"^### (TC-(?:FUNC|NF|EXC)-\d{3})", std, re.M))
check("TC ID = TC 본문 27건", len(tc_body) == 27 and ids(srs, TC) == tc_body,
      f"본문 {len(tc_body)}건 / SRS 참조 {len(ids(srs, TC))}건")

# ── 4. ERD ↔ DDL ────────────────────────────────────────
erd = {m.lower() for m in re.findall(r"^    ([A-Z_]+) \{", srs, re.M)}
ddl = set(re.findall(r"^CREATE TABLE (\w+)", srs, re.M))
check("ERD 엔터티 = DDL 테이블", erd == ddl, f"차이 {erd ^ ddl}")

fk = set(re.findall(r"REFERENCES (\w+)", srs))
check("FK 참조 대상 전건 정의됨", fk <= ddl, f"미정의 {fk - ddl}")

# ── 5. 게이트 데이터 실측 ↔ 문서 주장 ────────────────────
bc = json.loads(read(pathlib.Path("tools/boundary-cases.json")))
check("경계값 케이스 ≥ 200건", bc["total"] >= 200, f"실측 {bc['total']}건")
check("GTD 문서의 케이스 수 표기 일치", f"**{bc['total']}건**" in gtd,
      f"실측 {bc['total']}건")

pt = json.loads(read(pathlib.Path("tools/prohibited-terms.json")))
npat = sum(len(c["patterns"]) for c in pt["categories"])
check("GTD 문서의 패턴 수 표기 일치", f"패턴 **{npat}개**" in gtd, f"실측 {npat}개")

samples = json.loads(read(pathlib.Path("tools/scan-samples.json")))
check("GTD 문서의 샘플 수 표기 일치", f"**{len(samples)}건**" in gtd,
      f"실측 {len(samples)}건")

# ── 6. 태스크 리스트 ────────────────────────────────────
# 표의 첫 열(행 시작)에 있는 ID만 정의로 인정한다 — 선행 태스크 열과 구분
rows = re.findall(r"^\|\s*(?:🔴 )?((?:CT|MK|IN|DA|BE|FE|QA|TS|DS)-\d{3}[ab]?)\s*\|", task, re.M)
tids = set(rows)
check("태스크 ID 중복 없음", len(tids) == len(rows), f"정의 {len(rows)}건 / 고유 {len(tids)}건")
check("태스크 총계 표기 일치", f"**{len(rows)}** |" in task or f"**{len(rows)}**" in task,
      f"실측 {len(rows)}건")
deps = set(re.findall(r"(?:CT|MK|IN|DA|BE|FE|QA|TS|DS)-\d{3}[ab]?", task))
check("태스크 선행 참조가 실재함", deps <= tids | {"DA-001~010"},
      f"미정의 참조 {sorted(deps - tids)[:5]}")

# ── 6-2. 태스크 그래프 무결성 (build_task_graph.py 위임) ──
import subprocess
g = subprocess.run([sys.executable, "tools/build_task_graph.py"],
                   capture_output=True, text=True)
check("태스크 선행 참조 무결성", g.returncode == 0,
      [l for l in g.stdout.split("\n") if "❌" in l][:1])

# ── 7. 깨진 파일 참조 ───────────────────────────────────
stale = [n for n in ("cardfit-srs-v1_0", "cardfit-design-v1_0",
                     "cardfit-testcase-v1_0", "cardfit-gate-data-v1_0", "gate/")
         if any(n in t for t in (srs, sdd, std, gtd, task))]
check("구 파일명 참조 없음", not stale, f"잔여 {stale}")

# ── 출력 ────────────────────────────────────────────────
print(f"{'결과':<4} {'검사 항목':<38} 상세")
print("-" * 78)
for n, ok, d in checks:
    print(f"{'✅' if ok else '❌':<3} {n:<38} {d if not ok else ''}")
print("-" * 78)
print(f"검사 {len(checks)}건 / 실패 {len(fails)}건")
sys.exit(1 if fails else 0)
