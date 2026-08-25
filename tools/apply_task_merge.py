#!/usr/bin/env python3
"""태스크 병합 적용기 — tools/task_merge_map.json 을 원본 리스트에 적용해 표를 생성한다.

선행·후행·복잡도·차단 여부를 원본 그래프에서 계산한다. 수기로 적지 않는다.
"""
import re, json, sys, pathlib, collections

SRC = pathlib.Path("docs/[태스크 리스트] CardFit.md")
MAP = pathlib.Path("tools/task_merge_map.json")
ID  = r"(?:CT|MK|IN|DA|BE|FE|QA|TS|DS)-\d{3}[ab]?"
RANK = {"L": 0, "M": 1, "H": 2}

def parse_src(text):
    rows = {}
    for line in text.split("\n"):
        m = re.match(rf"^\|\s*(🔴 )?({ID})\s*\|(.*)$", line)
        if not m: continue
        c = line.split("|")
        if len(c) < 9: continue
        rows[m.group(2)] = dict(blocked=bool(m.group(1)), epic=c[2].strip(),
                                feat=c[3].strip(), srs=c[4].strip(),
                                deps=re.findall(ID, c[5]), cx=c[7].strip())
    return rows

def build(rows, groups):
    member = {m: g["id"] for g in groups for m in g["members"]}
    out = {}
    for g in groups:
        ms = [rows[m] for m in g["members"]]
        deps = sorted({member[d] for m in g["members"] for d in rows[m]["deps"]
                       if d in member and member[d] != g["id"]})
        srs = []
        for m in ms:
            for s in re.split(r"\s*·\s*", m["srs"]):
                s = s.strip()
                if s and s not in srs: srs.append(s)
        out[g["id"]] = dict(epic=g["epic"], name=g["name"], members=g["members"],
                            deps=deps, srs=srs,
                            cx=max((m["cx"] for m in ms), key=lambda x: RANK.get(x, 0)),
                            blocked=any(m["blocked"] for m in ms))
    blocks = collections.defaultdict(list)
    for gid, g in out.items():
        for d in g["deps"]: blocks[d].append(gid)
    for gid in out: out[gid]["blocks"] = sorted(blocks.get(gid, []))
    return out

def topo(out):
    done, layers = set(), []
    while len(done) < len(out):
        cur = sorted(g for g in out if g not in done
                     and all(d in done for d in out[g]["deps"]))
        if not cur: return layers, sorted(set(out) - done)
        layers.append(cur); done |= set(cur)
    return layers, []

def row(gid, g, max_srs=3):
    srs = " · ".join(g["srs"][:max_srs]) + (" 외" if len(g["srs"]) > max_srs else "")
    return (f"| {'🔴 ' if g['blocked'] else ''}**{gid}** | {g['epic']} | {g['name']} "
            f"| {', '.join(g['members'])} | {srs} "
            f"| {', '.join(g['deps']) or 'None'} | {', '.join(g['blocks']) or '—'} | {g['cx']} |")

if __name__ == "__main__":
    rows = parse_src(SRC.read_text(encoding="utf-8"))
    groups = json.loads(MAP.read_text(encoding="utf-8"))["groups"]
    missing = {m for g in groups for m in g["members"]} ^ set(rows)
    if missing:
        print(f"❌ 원본과 맵 불일치: {sorted(missing)[:8]}"); sys.exit(1)
    out = build(rows, groups)
    layers, cycle = topo(out)
    print(f"원본 {len(rows)}건 → 그룹 {len(out)}건 · 위상 계층 {len(layers)}개"
          + (f" · ⚠️ 순환 {cycle}" if cycle else ""))
    print(f"차단 그룹 {sum(1 for g in out.values() if g['blocked'])}개\n")
    if "--emit" in sys.argv:
        HDR = ("| Task ID | Epic (도메인) | Feature (기능명) | 구성 (원본) | 관련 SRS 섹션 "
               "| 선행 태스크 | 후행 태스크 (Blocks) | 복잡도 |\n"
               "| --- | --- | --- | --- | --- | --- | --- | :---: |")
        cur = None
        for gid in [g["id"] for g in groups]:
            pre = gid.split("-")[0]
            if pre != cur:
                print(f"\n<!--SECTION:{pre}-->\n{HDR}"); cur = pre
            print(row(gid, out[gid]))
