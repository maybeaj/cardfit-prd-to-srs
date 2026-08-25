#!/usr/bin/env python3
"""금지어 스캐너 — D8 / 배포 게이트 ② (TC-FUNC-009)

판정 규칙: allowlist를 먼저 제거한 뒤 patterns를 매칭한다.
block 심각도가 1건이라도 남으면 종료코드 1 → 배포 차단 (GR4).
"""
import json, re, sys, argparse, pathlib

def load(dic):
    d = json.loads(pathlib.Path(dic).read_text(encoding="utf-8"))
    cats = [(c["id"], c["name"], c["severity"],
             [re.compile(p) for p in c["patterns"]]) for c in d["categories"]]
    allow = [a["text"] for a in d["allowlist"]]
    return cats, allow

def scan(text, cats, allow):
    """allowlist 문구를 제거한 잔여 텍스트에만 금지 패턴을 적용한다."""
    residual = text
    for a in allow:
        residual = residual.replace(a, " ")
    hits = []
    for cid, name, sev, pats in cats:
        for p in pats:
            for m in p.finditer(residual):
                hits.append({"category": cid, "name": name, "severity": sev,
                             "matched": m.group(0)})
    return hits

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dict", default="gate/prohibited-terms.json")
    ap.add_argument("--samples", default="gate/scan-samples.json")
    a = ap.parse_args()
    cats, allow = load(a.dict)
    samples = json.loads(pathlib.Path(a.samples).read_text(encoding="utf-8"))

    fails = 0
    print(f"{'판정':<6} {'기대':<8} {'문구':<46} 적발")
    print("-" * 90)
    for s in samples:
        hits = scan(s["text"], cats, allow)
        blocked = any(h["severity"] == "block" for h in hits)
        expect_blocked = s["expect"] == "block"
        ok = blocked == expect_blocked
        if not ok: fails += 1
        cats_hit = ",".join(sorted({h["category"] for h in hits})) or "-"
        print(f"{'✅' if ok else '❌':<5} {s['expect']:<8} {s['text'][:44]:<46} {cats_hit}")
    print("-" * 90)
    print(f"샘플 {len(samples)}건 / 판정 불일치 {fails}건")
    sys.exit(1 if fails else 0)
