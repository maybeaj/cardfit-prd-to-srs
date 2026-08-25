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
CALC = D / "[계산 명세서] CardFit (한글).md"
FXT  = D / "[픽스처 데이터 명세] CardFit (한글).md"

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
for p in (SRS, SDD, STD, GTD, TASK, CALC, FXT):
    check(f"파일 존재: {p.name}", p.exists())
if fails:
    for n, ok, d in checks: print(f"{'✅' if ok else '❌'} {n}")
    sys.exit(1)

srs, sdd, std, gtd, task, calc, fxt = map(read, (SRS, SDD, STD, GTD, TASK, CALC, FXT))

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
rows = re.findall(r"^\|\s*(?:🔴 )?\*\*((?:CT|MK|IN|DA|BE|FE|QA|TS|DS)-\d{2})\*\*\s*\|", task, re.M)
tids = set(rows)
check("태스크 ID 중복 없음", len(tids) == len(rows), f"정의 {len(rows)}건 / 고유 {len(tids)}건")
check("태스크 총계 표기 일치", f"**{len(rows)}** |" in task or f"**{len(rows)}**" in task,
      f"실측 {len(rows)}건")
deps = set(re.findall(r"(?:CT|MK|IN|DA|BE|FE|QA|TS|DS)-\d{2}(?![0-9])", task))
check("태스크 선행 참조가 실재함", deps <= tids, f"미정의 참조 {sorted(deps - tids)[:5]}")

# 병합 커버리지 — 원본 142건이 그룹에 전건 편입됐는가
mm = json.loads(read(pathlib.Path("tools/task_merge_map.json")))
mem = [m for g in mm["groups"] for m in g["members"]]
check("그룹 맵 구성원 중복 0", len(mem) == len(set(mem)), f"구성원 {len(mem)} · 고유 {len(set(mem))}")
check("병합 그룹 수 = 태스크 표 행 수", len(mm["groups"]) == len(tids),
      f"맵 {len(mm['groups'])} · 표 {len(tids)}")

# ── 6-2. 태스크 그래프 무결성 (build_task_graph.py 위임) ──
import subprocess
g = subprocess.run([sys.executable, "tools/build_task_graph.py"],
                   capture_output=True, text=True)
check("태스크 선행 참조 무결성", g.returncode == 0,
      [l for l in g.stdout.split("\n") if "❌" in l][:1])

# ── 6-3. 이슈 명세 템플릿 준수 ───────────────────────────
SECT = ["## 🎯 Summary", "## 🔗 References (Spec & Context)",
        "## ✅ Task Breakdown (실행 계획)", "## 🧪 Acceptance Criteria (BDD/GWT)",
        "## ⚙️ Technical & Non-Functional Constraints",
        "## 🏁 Definition of Done (DoD)", "## 🚧 Dependencies & Blockers"]
for tf in sorted(pathlib.Path("docs/tasks").glob("*.md")) if pathlib.Path("docs/tasks").exists() else []:
    body = read(tf)
    blocks = re.findall(r"```markdown\n(.*?)\n```", body, re.S)
    bad = [b[:40] for b in blocks if not all(x in b for x in SECT)]
    gwt_bad = [b[:40] for b in blocks
               if len(re.findall(r"^Scenario \d+:", b, re.M)) < 2
               or len(re.findall(r"^- Given:", b, re.M)) != len(re.findall(r"^- Then:", b, re.M))]
    check(f"이슈 명세 템플릿 준수: {tf.name}", not bad and not gwt_bad and blocks,
          f"섹션누락 {len(bad)} · GWT불일치 {len(gwt_bad)} · 블록 {len(blocks)}")

# ── 6-4. 계산 명세 ↔ 게이트 파라미터 바인딩 ──────────────
PARAMS = {"abs_threshold": 3000, "rel_threshold": 0.10, "scenario_delta": 0.20}
check("경계값 파라미터 바인딩 완료", bc.get("params_bound") is True and bc["params"] == PARAMS,
      f"실측 {bc.get('params')}")
for label, val in (("절대 임계값", "월 3,000원"), ("상대 임계값", "상대 10%"),
                   ("증감 폭", "±20%")):
    check(f"CALC 문서 {label} 표기", val in calc, f"'{val}' 미표기")
check("SRS 10.3 미결 표기 소거", "🔴 미정" not in srs and "🔴 미확인" not in srs,
      "10.3에 🔴 잔존")
blocked_rows = re.findall(r"^\|\s*🔴", task, re.M)
check("태스크 리스트 착수 차단 0건", not blocked_rows, f"차단 행 {len(blocked_rows)}건")

# ── 6-5. 픽스처 실측 ↔ 문서 주장 ─────────────────────────
FX = pathlib.Path("tools/fixtures")
fx = {}
for name in ("card-products", "terms", "personas", "mydata-snapshots",
             "expected-results", "ai-cache", "demo-clock"):
    f = FX / f"{name}.json"
    check(f"픽스처 존재: {name}.json", f.exists())
    if f.exists():
        fx[name] = json.loads(read(f))
if len(fx) == 7:
    n_prod = len(fx["card-products"]["products"])
    n_psn = len(fx["personas"]["personas"])
    n_tx = sum(len(s["transactions"]) for s in fx["mydata-snapshots"]["snapshots"])
    check("FXT 문서의 카드 상품 수 표기 일치", f"**{n_prod}종**" in fxt, f"실측 {n_prod}종")
    check("FXT 문서의 페르소나 수 표기 일치", f"**{n_psn}인**" in fxt, f"실측 {n_psn}인")
    check("FXT 문서의 거래 건수 표기 일치", f"**{n_tx}건**" in fxt, f"실측 {n_tx}건")
    exp = {r["persona_id"]: r for r in fx["expected-results"]["results"]}
    ok = all(r["scenarios"] is None or
             r["scenarios"]["AS_EXPECTED"]["gating"] == r["expect"] for r in exp.values())
    check("픽스처 기대 결론 = 참조 계산기 실측", ok,
          [k for k, r in exp.items()
           if r["scenarios"] and r["scenarios"]["AS_EXPECTED"]["gating"] != r["expect"]])
    check("픽스처 계산 파라미터 = CALC 결정값",
          fx["card-products"]["params"]["abs_threshold"] == PARAMS["abs_threshold"]
          and fx["card-products"]["params"]["rel_threshold"] == PARAMS["rel_threshold"]
          and fx["card-products"]["params"]["scenario_delta"] == PARAMS["scenario_delta"],
          f"실측 {fx['card-products']['params']}")
    # 픽스처 문구 전건이 금지어 게이트를 통과하는가 (GR4)
    sys.path.insert(0, "tools")
    import importlib.util as _il
    _s = _il.spec_from_file_location("_scan", "tools/scan_prohibited_terms.py")
    _m = _il.module_from_spec(_s); _s.loader.exec_module(_m)
    cats, allow = _m.load("tools/prohibited-terms.json")
    texts = [x["text"] for x in fx["ai-cache"]["explanations"]] \
          + [x["summary"] for x in fx["ai-cache"]["term_summaries"]] \
          + [d["text"] for d in fx["terms"]["documents"]]
    blocked = [x for x in texts
               if any(h["severity"] == "block" for h in _m.scan(x, cats, allow))]
    check(f"픽스처 문구 금지어 0건 ({len(texts)}건 검사)", not blocked, f"적발 {len(blocked)}건")

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
