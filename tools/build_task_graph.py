#!/usr/bin/env python3
"""태스크 의존성 그래프 도구 — Blocks 역방향 생성 · 위상 정렬 · 순환 검사

선행 태스크 열에서 후행(Blocks) 관계를 계산한다. 수동 관리하지 않는다 —
선행 열이 바뀌면 --write 로 다시 생성해 어긋남을 막는다.
"""
import re, sys, argparse, pathlib, collections

TASKS = pathlib.Path("docs/[태스크 리스트] CardFit.md")
ID = r"(?:CT|MK|IN|DA|BE|FE|QA|TS|DS)-\d{2,3}[ab]?"
ROW = re.compile(rf"^\|\s*(?:🔴 )?\*?\*?({ID})\*?\*?\s*\|(.*)$")

def parse(text):
    rows = []
    for i, line in enumerate(text.split("\n")):
        m = ROW.match(line)
        if not m: continue
        cells = line.split("|")
        if len(cells) < 9: continue
        rows.append(dict(line=i, id=m.group(1), blocked="🔴" in cells[1],
                         deps=[d for d in re.findall(ID, cells[-3])],
                         raw=line))
    return rows

def graph(rows):
    ids = {r["id"] for r in rows}
    blocks = collections.defaultdict(list)
    dangling = []
    for r in rows:
        for d in r["deps"]:
            if d in ids: blocks[d].append(r["id"])
            else: dangling.append((r["id"], d))
    return ids, blocks, dangling

def topo(rows, ids):
    dep = {r["id"]: [d for d in r["deps"] if d in ids] for r in rows}
    done, layers = set(), []
    while len(done) < len(dep):
        cur = sorted(i for i in dep if i not in done and all(d in done for d in dep[i]))
        if not cur: return layers, sorted(set(dep) - done)   # 순환
        layers.append(cur); done |= set(cur)
    return layers, []

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true", help="후행 태스크 열을 문서에 반영")
    a = ap.parse_args()

    text = TASKS.read_text(encoding="utf-8")
    rows = parse(text)
    ids, blocks, dangling = graph(rows)
    layers, cycle = topo(rows, ids)

    print(f"태스크 {len(rows)}건 · 의존 엣지 {sum(len(v) for v in blocks.values())}개")
    print(f"위상 계층 {len(layers)}개" + (f" · ⚠️ 순환 {cycle}" if cycle else ""))
    if dangling:
        print(f"❌ 미정의 선행 참조 {len(dangling)}건: {dangling[:6]}")
    else:
        print("✅ 선행 참조 전건 실재")

    print("\n최다 차단 Top 8")
    for k, v in sorted(blocks.items(), key=lambda x: -len(x[1]))[:8]:
        print(f"  {k:<9} {len(v):2}건")

    if a.write:
        lines = text.split("\n")
        for r in rows:
            cells = lines[r["line"]].split("|")
            b = blocks.get(r["id"], [])
            cells.insert(-2, f" {', '.join(b) if b else '—'} ")
            lines[r["line"]] = "|".join(cells)
        # 헤더·구분선에도 열 추가
        out = []
        for l in lines:
            if l.startswith("| Task ID |") and "후행" not in l:
                c = l.split("|"); c.insert(-2, " 후행 태스크 (Blocks) "); l = "|".join(c)
            elif re.match(r"^\| --- \| --- \| --- \| --- \| --- \| :---: \|$", l):
                c = l.split("|"); c.insert(-2, " --- "); l = "|".join(c)
            out.append(l)
        TASKS.write_text("\n".join(out), encoding="utf-8")
        print("\n✅ 후행 태스크 열 반영 완료")
    sys.exit(1 if (dangling or cycle) else 0)
