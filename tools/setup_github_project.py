#!/usr/bin/env python3
"""GitHub Project 세팅 — 이슈 58건 등록 · 필드 생성 · 일정 값 주입

EXE-CARDFIT-001 v1.1의 AI 가속 수정판(29 작업일) 일정을 프로젝트 필드로 옮긴다.
로드맵 뷰는 gh CLI가 생성을 지원하지 않아 UI에서 설정한다(--help 참고).

전제: gh auth refresh -s project  (read:project · project 스코프)
사용:  python3 tools/setup_github_project.py [--dry-run]
"""
import json, subprocess, sys, pathlib, argparse, datetime, math, os, importlib.util

OWNER, NUMBER, REPO = "maybeaj", "1", "maybeaj/cardfit-prd-to-srs"
STATE = pathlib.Path("tools/.project-state.json")

def gh(*args, parse=True, tries=3, timeout=45):
    """gh 호출은 응답 없이 멈추는 일이 있다 — 타임아웃과 재시도를 건다."""
    last = ""
    for n in range(tries):
        try:
            r = subprocess.run(["gh", *args], capture_output=True, text=True, timeout=timeout)
        except subprocess.TimeoutExpired:
            last = f"{timeout}s 무응답"; print(f"    ⏱ 재시도 {n+1}/{tries} — {' '.join(args[:3])}", flush=True)
            continue
        if r.returncode == 0:
            return json.loads(r.stdout) if parse and r.stdout.strip() else r.stdout.strip()
        last = r.stderr.strip()[:200]
        print(f"    ↻ 재시도 {n+1}/{tries} — {last[:80]}", flush=True)
    raise SystemExit(f"❌ gh {' '.join(args[:3])}: {last}")

# ── 일정 산정 — 총괄 문서 6.5절의 계수를 그대로 옮긴다 ──────────────
DS   = {"DS-01","DS-02","DS-03","DS-04","DS-05"}
JUDG = {"BE-01","BE-02","BE-03","BE-05","BE-06","BE-07","BE-08","BE-09",
        "BE-15","BE-18","IN-08"}
VERI = {"IN-02","IN-03","IN-09","BE-10","QA-01","QA-02","QA-03","QA-04"}
FACT = lambda t: 0.70 if t in DS else 0.55 if t in JUDG else 0.80 if t in VERI else 0.35
TRACK_OF = lambda t: ("계약·Mock" if t[:2] in ("CT","MK") else "인프라·플랫폼" if t[:2]=="IN"
    else "데이터 계층" if t[:2]=="DA" else "디자인" if t[:2]=="DS"
    else "프론트엔드" if t[:2]=="FE" else "QA·테스트" if t[:2] in ("TS","QA")
    else "계산 도메인" if t in ("BE-06","BE-07","BE-08","BE-09","BE-10","BE-11","BE-12","BE-16")
    else "백엔드 도메인")
START = datetime.date(2026, 8, 31)

def workday(offset):
    d, n = START, 0
    while n < offset:
        d += datetime.timedelta(days=1)
        if d.weekday() < 5: n += 1
    while d.weekday() >= 5: d += datetime.timedelta(days=1)
    return d

def schedule():
    os.environ["TASK_SRC"] = "tools/task-source-v11.md"
    sp = importlib.util.spec_from_file_location("am", "tools/apply_task_merge.py")
    am = importlib.util.module_from_spec(sp); sp.loader.exec_module(am)
    rows = am.parse_src(open("tools/task-source-v11.md", encoding="utf-8").read())
    G = am.build(rows, json.loads(pathlib.Path("tools/task_merge_map.json").read_text(encoding="utf-8"))["groups"])
    items = {}
    for f in sorted(pathlib.Path("docs/tasks").glob("*.md")):
        b = f.read_text(encoding="utf-8")
        sec = b[b.index("## ✅ Task Breakdown"):b.index("## 🧪 Acceptance Criteria")]
        items[f.stem] = sec.count("- [ ]")
    CX = {"H":1.4, "M":1.0, "L":0.8}
    dur = {t: max(1, round(max(2, math.ceil(items[t]*0.45*CX[G[t]["cx"]])) * FACT(t))) for t in G}
    deps = {t: list(G[t]["deps"]) for t in G}
    lag = {("BE-17","FE-07"): math.floor(dur["BE-17"]*0.4)}          # 압축 레버 ④
    layers, _ = am.topo(G); flat = [t for l in layers for t in l]
    ES, EF = {}, {}
    for t in flat:
        ES[t] = max([EF[p]-lag.get((p,t),0) for p in deps[t]], default=0)
        EF[t] = ES[t] + dur[t]
    T = max(EF.values())
    blocks = {t: [] for t in deps}
    for t in deps:
        for p in deps[t]: blocks[p].append(t)
    LS, LF = {}, {}
    for t in reversed(flat):
        LF[t] = min([LS[s]+lag.get((t,s),0) for s in blocks[t]], default=T)
        LS[t] = LF[t] - dur[t]
    def end(t):
        d, n = workday(ES[t]), 1
        while n < dur[t]:
            d += datetime.timedelta(days=1)
            if d.weekday() < 5: n += 1
        return d
    return {t: dict(start=str(workday(ES[t])), end=str(end(t)), dur=dur[t],
                    track=TRACK_OF(t), week=f"W{ES[t]//5+1}", slack=LS[t]-ES[t])
            for t in G}, T

# ⚠️ SINGLE_SELECT 옵션을 나중에 updateProjectV2Field 로 재정의하면 옵션 ID가 새로
#    발급되어 **이미 설정된 값이 전부 초기화된다.** 옵션 범위는 처음부터 넉넉히 잡는다.
FIELDS = [("Start date","DATE",None), ("Target date","DATE",None),
          ("Track","SINGLE_SELECT","디자인,계약·Mock,인프라·플랫폼,데이터 계층,계산 도메인,백엔드 도메인,프론트엔드,QA·테스트"),
          ("Week","SINGLE_SELECT","W1,W2,W3,W4,W5,W6,W7,W8"),
          ("Duration","NUMBER",None), ("Slack","NUMBER",None)]

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    sched, T = schedule()
    imap = json.loads(pathlib.Path("tools/issue-map.json").read_text(encoding="utf-8"))
    print(f"일정 산정 — 총 {T} 작업일 · 태스크 {len(sched)}건 · 이슈 {len(imap)}건", flush=True)
    if a.dry_run:
        for t in sorted(sched, key=lambda x: sched[x]["start"]):
            s = sched[t]
            print(f"  #{imap[t]:>2} {t} {s['track']:<8} {s['start']}~{s['end']} "
                  f"({s['dur']}일) {s['week']} slack {s['slack']}")
        return

    proj = gh("project","view",NUMBER,"--owner",OWNER,"--format","json")
    pid = proj["id"]; print(f"프로젝트: {proj['title']} ({pid})", flush=True)

    have = {f["name"]: f for f in gh("project","field-list",NUMBER,"--owner",OWNER,
                                     "--format","json","--limit","50")["fields"]}
    for name, dtype, opts in FIELDS:
        if name in have: continue
        cmd = ["project","field-create",NUMBER,"--owner",OWNER,"--name",name,"--data-type",dtype]
        if opts: cmd += ["--single-select-options", opts]
        gh(*cmd, parse=False); print(f"  필드 생성: {name}", flush=True)
    F = {f["name"]: f for f in gh("project","field-list",NUMBER,"--owner",OWNER,
                                  "--format","json","--limit","50")["fields"]}

    existing = {i.get("content",{}).get("number"): i["id"]
                for i in gh("project","item-list",NUMBER,"--owner",OWNER,
                            "--format","json","--limit","200")["items"] if i.get("content")}
    for t, num in sorted(imap.items(), key=lambda x: x[1]):
        if num in existing: continue
        gh("project","item-add",NUMBER,"--owner",OWNER,
           "--url",f"https://github.com/{REPO}/issues/{num}", parse=False)
        print(f"  추가: #{num} {t}", flush=True)
    raw = gh("project","item-list",NUMBER,"--owner",OWNER,"--format","json","--limit","200")["items"]
    items = {i["content"]["number"]: i["id"] for i in raw if i.get("content")}
    done_already = {i["content"]["number"] for i in raw
                    if i.get("content") and i.get("start date") and i.get("track")}
    if done_already:
        print(f"  재개 — 값이 이미 채워진 {len(done_already)}건은 건너뛴다", flush=True)

    def opt_id(field, value):
        return next(o["id"] for o in F[field]["options"] if o["name"] == value)
    for t, num in sorted(imap.items(), key=lambda x: x[1]):
        if num in done_already: continue
        s = sched[t]; iid = items[num]
        for fname, flag, val in [("Start date","--date",s["start"]), ("Target date","--date",s["end"]),
                                 ("Duration","--number",str(s["dur"])), ("Slack","--number",str(s["slack"])),
                                 ("Track","--single-select-option-id",opt_id("Track",s["track"])),
                                 ("Week","--single-select-option-id",opt_id("Week",s["week"]))]:
            gh("project","item-edit","--id",iid,"--project-id",pid,
               "--field-id",F[fname]["id"], flag, val, parse=False)
        print(f"  필드 설정: #{num} {t}", flush=True)
    print(f"\n✅ 완료 — 아이템 {len(items)}건 · 필드 {len(FIELDS)}종")
    print("로드맵 뷰는 UI에서 설정한다 — Layout: Roadmap · Date fields: Start date / Target date")

if __name__ == "__main__":
    main()
