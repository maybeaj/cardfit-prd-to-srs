#!/usr/bin/env python3
"""경계값 테스트 케이스 생성기 — D8 / 배포 게이트 ① (TC-NF-002)

SRS의 계산 규칙에서 경계 차원을 도출해 케이스를 생성한다.
단독 경계값 전수 + 상호작용이 실재하는 차원 쌍의 pairwise 조합.

D2(게이팅 임계값)·D5(시나리오 증감 폭)은 파라미터다.
확정 전에는 심볼로 남고, 확정 후 --abs/--rel/--delta로 주입해 기대값이 바인딩된다.
"""
import json, argparse, itertools

# ── 경계 차원 정의 ─────────────────────────────────────────
# 각 값: (식별자, 설명, 기대 동작)
DIMS = {
    "perf_tier": [  # 실적구간 (REQ-FUNC-003)
        ("TIER_BELOW_MIN",      "최저 구간 하한 미달 (0원)",        "혜택 미적용"),
        ("TIER_MIN_MINUS_1",    "구간 하한 -1원",                  "직전 구간 적용"),
        ("TIER_MIN_EXACT",      "구간 하한 정확히",                "해당 구간 적용"),
        ("TIER_MIN_PLUS_1",     "구간 하한 +1원",                  "해당 구간 적용"),
        ("TIER_MAX_MINUS_1",    "구간 상한 -1원",                  "해당 구간 적용"),
        ("TIER_MAX_EXACT",      "구간 상한 정확히",                "해당 구간 적용"),
        ("TIER_MAX_PLUS_1",     "구간 상한 +1원",                  "다음 구간 적용"),
        ("TIER_ABOVE_TOP",      "최고 구간 초과",                  "최고 구간 적용"),
    ],
    "discount_cap": [  # 통합할인한도
        ("CAP_MINUS_1",   "혜택 합계 = 한도 -1원", "전액 지급"),
        ("CAP_EXACT",     "혜택 합계 = 한도",      "전액 지급"),
        ("CAP_PLUS_1",    "혜택 합계 = 한도 +1원", "한도까지만 지급"),
        ("CAP_ZERO",      "한도 0원",              "혜택 0원"),
        ("CAP_UNLIMITED", "한도 없음 (NULL)",      "전액 지급"),
    ],
    "annual_fee": [  # 연회비 + 사용자 제약
        ("FEE_ZERO",             "연회비 0원",              "전환비용 ① = 0"),
        ("FEE_NORMAL",           "일반 연회비",             "전환비용 ①에 반영"),
        ("FEE_CAP_MINUS_1",      "사용자 연회비 상한 -1원", "제약 통과"),
        ("FEE_CAP_EXACT",        "사용자 연회비 상한 정확히","제약 통과"),
        ("FEE_CAP_PLUS_1",       "사용자 연회비 상한 +1원", "후보에서 제외"),
        ("FEE_SUM_OVER_CAP",     "조합 합산이 상한 초과",   "후보에서 제외"),
    ],
    "exclusion": [  # 제외항목
        ("EXC_NONE",         "제외 없음",                    "전액 인정"),
        ("EXC_ALL",          "전액 제외",                    "실적·혜택 0"),
        ("EXC_PARTIAL",      "일부 업종 제외",               "제외분 차감"),
        ("EXC_PERF_ONLY",    "실적 산정에만 제외 적용",      "혜택은 인정"),
        ("EXC_BENEFIT_ONLY", "혜택 적용에만 제외 적용",      "실적은 인정"),
    ],
    "scenario": [  # 시나리오 (D5 파라미터)
        ("SC_LESS",        "적게 — 입력 × (1 - delta)", "독립 계산"),
        ("SC_AS_EXPECTED", "예상대로 — 입력값 그대로",  "기본 탭"),
        ("SC_MORE",        "많이 — 입력 × (1 + delta)", "독립 계산"),
    ],
    "gating": [  # 게이팅 임계값 (D2 파라미터)
        ("GATE_ABS_MINUS_1",  "Net Benefit = 절대 임계 -1원",       "KEEP_CURRENT"),
        ("GATE_ABS_EXACT",    "Net Benefit = 절대 임계 정확히",     "RECOMMEND_CHANGE"),
        ("GATE_ABS_PLUS_1",   "Net Benefit = 절대 임계 +1원",       "RECOMMEND_CHANGE"),
        ("GATE_REL_MINUS",    "상대 임계 미달",                     "KEEP_CURRENT"),
        ("GATE_REL_EXACT",    "상대 임계 정확히",                   "RECOMMEND_CHANGE"),
        ("GATE_ABS_OK_REL_NG","절대 통과 · 상대 미달",              "KEEP_CURRENT"),
        ("GATE_ABS_NG_REL_OK","절대 미달 · 상대 통과",              "KEEP_CURRENT"),
        ("GATE_NET_NEGATIVE", "Net Benefit 음수",                   "KEEP_CURRENT"),
    ],
    "allocation": [  # 배분 나눗셈 (오차 ≤ 1원)
        ("ALLOC_EXACT",     "총액이 카드 수로 나누어떨어짐", "오차 0원"),
        ("ALLOC_REM_1",     "1원 남음",                      "오차 ≤ 1원"),
        ("ALLOC_REM_2",     "2원 남음",                      "오차 ≤ 1원"),
        ("ALLOC_THIRD",     "3분할 (0.333… 반복)",           "오차 ≤ 1원"),
    ],
    "expiry": [  # 만료·최신성
        ("EXP_DAY_29",        "기준일 +29일",              "유효"),
        ("EXP_DAY_30",        "기준일 +30일",              "만료"),
        ("EXP_DAY_31",        "기준일 +31일",              "만료"),
        ("EXP_RULE_SAME",     "rule_version 동일",         "유효"),
        ("EXP_RULE_CHANGED",  "rule_version 변경",         "만료"),
        ("EXP_FRESH_29",      "verified_at 29일 경과",     "계산 대상"),
        ("EXP_FRESH_30",      "verified_at 30일 경과",     "계산 대상"),
        ("EXP_FRESH_31",      "verified_at 31일 경과",     "계산 대상 제외"),
    ],
    "card_count": [  # 보유 카드 수
        ("CARD_0",  "0장",  "계산 불가 — 필수 데이터 누락"),
        ("CARD_1",  "1장",  "계산 가능"),
        ("CARD_2",  "2장",  "조합 탐색 최소"),
        ("CARD_5",  "5장",  "일반"),
        ("CARD_10", "10장", "일반 상한"),
        ("CARD_20", "20장", "Won't 범위 경계 — 성능 관측용"),
    ],
}

# 상호작용이 실재하는 차원 쌍만 pairwise 조합한다 (전체 데카르트 곱은 불필요)
PAIRS = [
    ("perf_tier", "exclusion"),    # 제외항목이 실적 산정에 영향
    ("perf_tier", "scenario"),     # 시나리오별 지출이 실적구간을 바꾼다
    ("discount_cap", "scenario"),  # 지출 증감이 한도 도달 여부를 바꾼다
    ("gating", "allocation"),      # 게이팅 통과 후 배분 정합성
    ("gating", "annual_fee"),      # 연회비가 전환비용을 통해 Net Benefit에 영향
    ("expiry", "card_count"),      # 카드마다 rule_version이 달라 만료 판정이 갈린다
]

def build(abs_th=None, rel_th=None, delta=None):
    cases, seq = [], 0
    def sym(v): return v if v is not None else "TBD"

    # ① 단독 경계값 — 전 차원 전수
    for dim, vals in DIMS.items():
        for vid, desc, expect in vals:
            seq += 1
            cases.append({
                "case_id": f"BC-{seq:04d}", "kind": "single", "dimension": dim,
                "factors": {dim: vid}, "description": desc, "expected": expect,
                "params": {"abs_threshold": sym(abs_th), "rel_threshold": sym(rel_th),
                           "scenario_delta": sym(delta)},
                "requirement": REQ_OF[dim],
            })
    # ② pairwise — 상호작용 쌍
    for d1, d2 in PAIRS:
        for (v1, s1, e1), (v2, s2, e2) in itertools.product(DIMS[d1], DIMS[d2]):
            seq += 1
            cases.append({
                "case_id": f"BC-{seq:04d}", "kind": "pair", "dimension": f"{d1}×{d2}",
                "factors": {d1: v1, d2: v2},
                "description": f"{s1} + {s2}", "expected": f"{e1} / {e2}",
                "params": {"abs_threshold": sym(abs_th), "rel_threshold": sym(rel_th),
                           "scenario_delta": sym(delta)},
                "requirement": f"{REQ_OF[d1]}·{REQ_OF[d2]}",
            })
    return cases

REQ_OF = {
    "perf_tier": "REQ-FUNC-003", "discount_cap": "REQ-FUNC-003",
    "annual_fee": "REQ-FUNC-004", "exclusion": "REQ-FUNC-003",
    "scenario": "REQ-FUNC-003", "gating": "REQ-FUNC-004",
    "allocation": "REQ-FUNC-005", "expiry": "REQ-EXC-006",
    "card_count": "REQ-FUNC-003",
}

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--abs", dest="abs_th", type=int, default=None, help="D2 절대 임계값(원)")
    ap.add_argument("--rel", dest="rel_th", type=float, default=None, help="D2 상대 임계값(비율)")
    ap.add_argument("--delta", type=float, default=None, help="D5 시나리오 증감 폭(비율)")
    ap.add_argument("-o", "--out", default="gate/boundary-cases.json")
    a = ap.parse_args()
    cases = build(a.abs_th, a.rel_th, a.delta)
    bound = all(v is not None for v in (a.abs_th, a.rel_th, a.delta))
    doc = {
        "spec": "STD-CARDFIT-001 D8 / 배포 게이트 ① (TC-NF-002)",
        "version": "1.0",
        "params_bound": bound,
        "params": {"abs_threshold": a.abs_th, "rel_threshold": a.rel_th, "scenario_delta": a.delta},
        "total": len(cases),
        "by_kind": {k: sum(1 for c in cases if c["kind"] == k) for k in ("single", "pair")},
        "by_dimension": {d: sum(1 for c in cases if d in c["factors"]) for d in DIMS},
        "cases": cases,
    }
    with open(a.out, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=1)
    print(f"생성: {len(cases)}건 → {a.out}")
    print(f"  단독 {doc['by_kind']['single']}건 / 조합 {doc['by_kind']['pair']}건")
    print(f"  파라미터 바인딩: {'완료' if bound else '미완 (D2·D5 확정 전)'}")
    print(f"  게이트 요구 200건: {'✅ 충족' if len(cases) >= 200 else '❌ 미달'}")
