#!/usr/bin/env python3
"""픽스처 데이터 생성기 — FXT-CARDFIT-001 / 의존성 D1·D4·D11·D13·D14 해소용.

외부 연동 없이 시연이 성립하도록 카드상품 카탈로그·마이데이터 스냅샷·약관·AI 산출물을
사전 생성한다. 생성물이 CALC-CARDFIT-001의 결론(유지/변경)을 실제로 만들어내는지
같은 파일 안의 참조 계산기로 검증한다 — 검증 없이 내보내면 시연에서 어긋난다.

사용:  python3 tools/generate_fixtures.py [-o tools/fixtures]
"""
import argparse, json, pathlib, random, datetime, itertools

SPEC_VERSION = "1.0"
RULE_SPEC = "CALC-CARDFIT-001 v1.0"
DEMO_NOW = datetime.date(2026, 8, 25)          # 데모 클럭 기준일 — 실시간 now()를 쓰지 않는다
SEED = 20260825

# ── 계산 파라미터 (CALC-CARDFIT-001 1장) ──────────────────────────
ABS_TH, REL_TH, DELTA = 3000, 0.10, 0.20
COST_REBUILD, COST_EXEC = 5000, 10000
CUT_HELD, MAX_CANDIDATES, NEW_POOL = 8, 20, 3
SCENARIOS = {"LESS": 0.8, "AS_EXPECTED": 1.0, "MORE": 1.2}

# ── 카테고리 ──────────────────────────────────────────────────────
CATEGORIES = {
    "FOOD": "식비", "CAFE": "카페", "DELIVERY": "배달", "MART": "마트",
    "CONVENIENCE": "편의점", "TRANSPORT": "대중교통", "GAS": "주유",
    "SHOPPING": "쇼핑", "ONLINE": "온라인쇼핑", "TELECOM": "통신",
    "UTILITY": "공과금", "MEDICAL": "의료", "EDUCATION": "교육",
    "TRAVEL": "여행", "ENTERTAINMENT": "문화",
}
MERCHANTS = {
    "FOOD": ["김밥천국 역삼점", "한솥도시락 선릉점", "본죽 논현점", "미분당 강남점"],
    "CAFE": ["스타벅스 테헤란로점", "메가커피 역삼점", "투썸플레이스 삼성점"],
    "DELIVERY": ["배달앱 결제", "요기요 결제", "쿠팡이츠 결제"],
    "MART": ["이마트 성수점", "홈플러스 강동점", "롯데마트 서초점"],
    "CONVENIENCE": ["GS25 역삼점", "CU 논현점", "세븐일레븐 삼성점"],
    "TRANSPORT": ["티머니 충전", "서울교통공사", "카카오T 택시"],
    "GAS": ["SK에너지 삼성주유소", "GS칼텍스 논현주유소"],
    "SHOPPING": ["무신사", "자라 코엑스점", "올리브영 강남점"],
    "ONLINE": ["쿠팡", "네이버페이", "11번가"],
    "TELECOM": ["SKT 통신요금", "KT 통신요금", "LGU+ 통신요금"],
    "UTILITY": ["한국전력공사", "서울도시가스", "수도요금"],
    "MEDICAL": ["연세이비인후과", "강남약국", "서울치과"],
    "EDUCATION": ["윈터스쿨", "교보문고", "인프런"],
    "TRAVEL": ["대한항공", "야놀자", "아고다"],
    "ENTERTAINMENT": ["CGV 강남", "넷플릭스", "예스24 공연"],
}

# ── 카드 상품 카탈로그 ────────────────────────────────────────────
# 카드사명은 실명, 상품명은 상품 유형을 나타내는 가공명이다(FXT 2.1 면책).
# 혜택 구조(실적 구간·통합한도·제외항목)는 공개 약관의 일반적 형태를 근사한 값이다.
ISSUERS = ["신한카드", "삼성카드", "현대카드", "KB국민카드",
           "롯데카드", "하나카드", "우리카드", "NH농협카드"]

def product(pid, issuer, name, fee, tiers, cat_caps, exclusions, ver="2026-08-01"):
    return dict(card_product_id=pid, issuer=issuer, name=name, annual_fee=fee,
                tiers=tiers, category_caps=cat_caps, exclusions=exclusions,
                rule_version=f"{ver}-{pid.lower()}", exclusion_mode="BOTH")

def T(min_spend, cap, rates):
    return {"min_spend": min_spend, "monthly_cap": cap, "rates": rates}

CATALOG = [
    # ── 생활할인형 (식비·카페·편의점 중심) ──
    product("SHC-LIFE", "신한카드", "생활할인형", 15000,
            [T(0, 0, {}), T(300000, 20000, {"FOOD": .07, "CAFE": .10, "CONVENIENCE": .05, "MART": .03}),
             T(700000, 40000, {"FOOD": .10, "CAFE": .10, "CONVENIENCE": .07, "MART": .05})],
            {"CAFE": 10000}, ["UTILITY", "TELECOM"]),
    product("SSC-LIFE", "삼성카드", "생활적립형", 10000,
            [T(0, 0, {}), T(400000, 25000, {"FOOD": .05, "MART": .07, "DELIVERY": .07, "CONVENIENCE": .05}),
             T(800000, 45000, {"FOOD": .07, "MART": .10, "DELIVERY": .10, "CONVENIENCE": .05})],
            {"DELIVERY": 12000}, ["UTILITY"]),
    product("KBC-LIFE", "KB국민카드", "생필품형", 12000,
            [T(0, 0, {}), T(300000, 22000, {"MART": .07, "CONVENIENCE": .07, "FOOD": .03}),
             T(600000, 38000, {"MART": .10, "CONVENIENCE": .10, "FOOD": .05})],
            {"MART": 15000}, ["UTILITY", "MEDICAL"]),
    # ── 교통·주유형 ──
    product("WRC-MOVE", "우리카드", "교통주유형", 8000,
            [T(0, 0, {}), T(300000, 18000, {"TRANSPORT": .10, "GAS": .07, "CONVENIENCE": .03}),
             T(600000, 32000, {"TRANSPORT": .15, "GAS": .10, "CONVENIENCE": .05})],
            {"TRANSPORT": 12000}, ["UTILITY", "TELECOM"]),
    product("NHC-MOVE", "NH농협카드", "출퇴근형", 6000,
            [T(0, 0, {}), T(250000, 15000, {"TRANSPORT": .10, "CAFE": .05, "FOOD": .03}),
             T(500000, 28000, {"TRANSPORT": .12, "CAFE": .07, "FOOD": .05})],
            {}, ["UTILITY"]),
    product("HDC-MOVE", "현대카드", "드라이브형", 20000,
            [T(0, 0, {}), T(500000, 25000, {"GAS": .10, "TRANSPORT": .05, "TRAVEL": .05}),
             T(900000, 50000, {"GAS": .15, "TRANSPORT": .07, "TRAVEL": .07})],
            {"GAS": 20000}, ["UTILITY", "TELECOM"]),
    # ── 온라인·쇼핑형 ──
    product("HNC-ONLINE", "하나카드", "온라인쇼핑형", 15000,
            [T(0, 0, {}), T(400000, 25000, {"ONLINE": .07, "SHOPPING": .05, "DELIVERY": .05}),
             T(800000, 45000, {"ONLINE": .10, "SHOPPING": .07, "DELIVERY": .07})],
            {"ONLINE": 20000}, ["UTILITY"]),
    product("LTC-ONLINE", "롯데카드", "이커머스형", 12000,
            [T(0, 0, {}), T(300000, 20000, {"ONLINE": .07, "SHOPPING": .07, "ENTERTAINMENT": .05}),
             T(700000, 40000, {"ONLINE": .10, "SHOPPING": .10, "ENTERTAINMENT": .07})],
            {"SHOPPING": 15000}, ["UTILITY", "TELECOM"]),
    product("SHC-ONLINE", "신한카드", "디지털형", 18000,
            [T(0, 0, {}), T(500000, 30000, {"ONLINE": .10, "ENTERTAINMENT": .10, "TELECOM": .05}),
             T(1000000, 55000, {"ONLINE": .12, "ENTERTAINMENT": .12, "TELECOM": .07})],
            {"ENTERTAINMENT": 10000}, ["UTILITY"]),
    # ── 통신·공과금형 ──
    product("KBC-FIXED", "KB국민카드", "고정지출형", 10000,
            [T(0, 0, {}), T(300000, 18000, {"TELECOM": .10, "UTILITY": .05, "MEDICAL": .05}),
             T(600000, 30000, {"TELECOM": .15, "UTILITY": .07, "MEDICAL": .07})],
            {"TELECOM": 8000}, []),
    product("SSC-FIXED", "삼성카드", "납부형", 0,
            [T(0, 0, {}), T(300000, 12000, {"UTILITY": .05, "TELECOM": .05}),
             T(700000, 22000, {"UTILITY": .07, "TELECOM": .07})],
            {}, []),
    product("WRC-FIXED", "우리카드", "관리비형", 5000,
            [T(0, 0, {}), T(250000, 15000, {"UTILITY": .07, "TELECOM": .05, "EDUCATION": .05}),
             T(550000, 26000, {"UTILITY": .10, "TELECOM": .07, "EDUCATION": .07})],
            {"UTILITY": 10000}, []),
    # ── 프리미엄·여행형 ──
    product("HDC-PREM", "현대카드", "프리미엄형", 100000,
            [T(0, 30000, {"TRAVEL": .05, "SHOPPING": .03}),
             T(1000000, 80000, {"TRAVEL": .10, "SHOPPING": .07, "FOOD": .05, "CAFE": .05})],
            {}, []),
    product("LTC-TRAVEL", "롯데카드", "여행적립형", 30000,
            [T(0, 0, {}), T(600000, 35000, {"TRAVEL": .10, "TRANSPORT": .05, "SHOPPING": .05}),
             T(1200000, 60000, {"TRAVEL": .12, "TRANSPORT": .07, "SHOPPING": .07})],
            {"TRAVEL": 30000}, ["UTILITY", "TELECOM"]),
    product("HNC-PREM", "하나카드", "마일리지형", 50000,
            [T(0, 20000, {"TRAVEL": .05}),
             T(800000, 60000, {"TRAVEL": .10, "ONLINE": .05, "FOOD": .05})],
            {}, ["UTILITY"]),
    # ── 무연회비·기본형 ──
    product("NHC-BASIC", "NH농협카드", "무연회비형", 0,
            [T(0, 0, {}), T(200000, 10000, {"FOOD": .03, "CAFE": .03, "TRANSPORT": .03, "MART": .03})],
            {}, ["UTILITY", "TELECOM"]),
    product("KBC-BASIC", "KB국민카드", "기본형", 0,
            [T(0, 0, {}), T(300000, 12000, {"FOOD": .03, "ONLINE": .03, "CONVENIENCE": .03})],
            {}, ["UTILITY"]),
    product("SHC-BASIC", "신한카드", "첫카드형", 0,
            [T(0, 0, {}), T(200000, 10000, {"CAFE": .05, "CONVENIENCE": .05, "TRANSPORT": .03})],
            {"CAFE": 5000}, ["UTILITY", "TELECOM"]),
    # ── 육아·의료·교육형 ──
    product("SSC-CARE", "삼성카드", "육아교육형", 15000,
            [T(0, 0, {}), T(400000, 22000, {"EDUCATION": .10, "MEDICAL": .07, "MART": .05}),
             T(800000, 40000, {"EDUCATION": .12, "MEDICAL": .10, "MART": .07})],
            {"EDUCATION": 15000}, ["UTILITY"]),
    product("WRC-CARE", "우리카드", "의료형", 12000,
            [T(0, 0, {}), T(350000, 20000, {"MEDICAL": .10, "EDUCATION": .05, "FOOD": .03}),
             T(700000, 35000, {"MEDICAL": .12, "EDUCATION": .07, "FOOD": .05})],
            {"MEDICAL": 12000}, ["UTILITY", "TELECOM"]),
    # ── 외식·문화형 ──
    product("HDC-DINE", "현대카드", "외식형", 20000,
            [T(0, 0, {}), T(500000, 25000, {"FOOD": .10, "DELIVERY": .07, "CAFE": .05}),
             T(900000, 45000, {"FOOD": .12, "DELIVERY": .10, "CAFE": .07})],
            {"FOOD": 20000}, ["UTILITY"]),
    product("LTC-CULT", "롯데카드", "문화형", 10000,
            [T(0, 0, {}), T(300000, 18000, {"ENTERTAINMENT": .10, "SHOPPING": .05, "CAFE": .05}),
             T(600000, 32000, {"ENTERTAINMENT": .15, "SHOPPING": .07, "CAFE": .07})],
            {"ENTERTAINMENT": 12000}, ["UTILITY", "TELECOM"]),
    product("NHC-DINE", "NH농협카드", "동네상권형", 8000,
            [T(0, 0, {}), T(300000, 18000, {"FOOD": .07, "MART": .05, "CONVENIENCE": .05}),
             T(600000, 30000, {"FOOD": .10, "MART": .07, "CONVENIENCE": .07})],
            {}, ["UTILITY"]),
    product("HNC-DINE", "하나카드", "미식형", 25000,
            [T(0, 0, {}), T(600000, 28000, {"FOOD": .10, "CAFE": .10, "DELIVERY": .05}),
             T(1000000, 48000, {"FOOD": .12, "CAFE": .12, "DELIVERY": .07})],
            {"FOOD": 18000}, ["UTILITY", "TELECOM"]),
]
BY_ID = {p["card_product_id"]: p for p in CATALOG}

# ── 페르소나 ──────────────────────────────────────────────────────
# expect: 시연에서 나와야 하는 결론. 참조 계산기가 이를 검증한다.
PERSONAS = [
    dict(persona_id="P1", name="김하늘", age_band="30대", job="직장인",
         summary="보유 2장이 지출 구조를 이미 덮는다 — 개선 후보가 없는 명백한 유지",
         held=["SHC-LIFE", "WRC-MOVE"], expect="KEEP_CURRENT",
         spend={"FOOD": 480000, "CAFE": 95000, "TRANSPORT": 88000, "CONVENIENCE": 70000,
                "MART": 150000, "ONLINE": 120000, "TELECOM": 55000, "UTILITY": 90000},
         constraints=dict(max_cards=2, annual_fee_cap=40000, allow_new=True),
         consent="CONSENTED", note="유지 결론의 기본형 — 절대 기준부터 미달"),
    dict(persona_id="P2", name="이도현", age_band="40대", job="영업직",
         summary="개선분이 절대 기준은 넘지만 상대 10%에 못 미친다 — 임계 근처 유지",
         held=["HDC-MOVE", "KBC-FIXED"], expect="KEEP_CURRENT",
         spend={"GAS": 500000, "TRAVEL": 200000, "TRANSPORT": 150000, "FOOD": 150000,
                "UTILITY": 150000, "MEDICAL": 120000, "TELECOM": 100000, "CONVENIENCE": 60000},
         constraints=dict(max_cards=3, annual_fee_cap=40000, allow_new=True),
         consent="CONSENTED", note="게이팅 두 조건 중 절대 기준만 통과하는 경계 사례 (GR2 감시 대상)"),
    dict(persona_id="P3", name="박서윤", age_band="30대", job="프리랜서",
         summary="연회비 10만원 프리미엄 카드가 제 값을 못 한다 — 해지만으로 개선",
         held=["HDC-PREM", "LTC-ONLINE", "NHC-BASIC"], expect="RECOMMEND_CHANGE",
         spend={"ONLINE": 240000, "DELIVERY": 180000, "FOOD": 150000, "TRANSPORT": 120000,
                "ENTERTAINMENT": 100000, "MEDICAL": 80000, "TELECOM": 70000},
         constraints=dict(max_cards=3, annual_fee_cap=30000, allow_new=False),
         consent="CONSENTED", note="allow_new=false · 전환비용이 음수(연회비 절감)인 변경 결론"),
    dict(persona_id="P4", name="정민재", age_band="20대", job="사회초년생",
         summary="신규 1장을 더하면 개선폭이 크다 — 신규 발급 포함 변경",
         held=["SHC-BASIC"], expect="RECOMMEND_CHANGE",
         spend={"FOOD": 420000, "CAFE": 160000, "DELIVERY": 220000, "CONVENIENCE": 120000,
                "TRANSPORT": 95000, "ONLINE": 180000, "TELECOM": 50000},
         constraints=dict(max_cards=2, annual_fee_cap=30000, allow_new=True),
         consent="CONSENTED", note="북극성 지표(조합안 선택률) 시연 경로"),
    dict(persona_id="P5", name="최유진", age_band="50대", job="자영업",
         summary="동의 만료 · 수집 장애 · 근거 미달을 재현하는 예외 전용",
         held=["KBC-LIFE", "SSC-FIXED"], expect="EXCEPTION",
         spend={"FOOD": 300000, "MART": 400000, "UTILITY": 200000, "TELECOM": 70000,
                "MEDICAL": 90000, "TRANSPORT": 40000},
         constraints=dict(max_cards=4, annual_fee_cap=60000, allow_new=True),
         consent="EXPIRED", note="CF 6종 전건과 REQ-EXC-001~006 경로"),
]

# ══════════════════════════════════════════════════════════════════
# 참조 계산기 — CALC-CARDFIT-001 2~4장을 그대로 옮긴 것.
# 목적은 픽스처 검증이며, 제품 구현(BE-06~08)을 대체하지 않는다.
# ══════════════════════════════════════════════════════════════════
def tier_of(card, eligible_total):
    chosen = card["tiers"][0]
    for t in card["tiers"]:
        if eligible_total >= t["min_spend"]:
            chosen = t
    return chosen

def evaluate(cards, spend):
    """조합의 월 Gross Benefit과 배분을 산출한다 (S1~S6 · RE-8 택일)."""
    state = {}
    for c in cards:
        elig = {k: v for k, v in spend.items() if k not in c["exclusions"]}
        t = tier_of(c, sum(elig.values()))
        state[c["card_product_id"]] = dict(card=c, tier=t, eligible=elig,
                                           cap_left=t["monthly_cap"],
                                           cat_left=dict(c["category_caps"]))
    alloc, gross = [], 0
    for cat, amt in sorted(spend.items(), key=lambda kv: (-kv[1], kv[0])):
        best = None
        for cid, s in state.items():
            if cat not in s["eligible"]:
                continue
            rate = s["tier"]["rates"].get(cat, 0)
            if rate <= 0:
                continue
            val = int(amt * rate)                                   # floor
            val = min(val, s["cat_left"].get(cat, val), s["cap_left"])
            if val <= 0:
                continue
            key = (-val, -rate, s["card"]["annual_fee"], cid)       # 동점 처리 (2.5절)
            if best is None or key < best[0]:
                best = (key, cid, val)
        if best is None:
            alloc.append(dict(category=cat, amount=amt, card_product_id=None, benefit=0))
            continue
        _, cid, val = best
        s = state[cid]
        s["cap_left"] -= val
        if cat in s["cat_left"]:
            s["cat_left"][cat] -= val
        gross += val
        alloc.append(dict(category=cat, amount=amt, card_product_id=cid, benefit=val))
    return gross, alloc, {cid: s["tier"]["min_spend"] for cid, s in state.items()}

def primary_cats(alloc):
    top = {}
    for a in alloc:
        if a["card_product_id"] and a["benefit"] > 0:
            cur = top.get(a["card_product_id"])
            if cur is None or a["benefit"] > cur[1]:
                top[a["card_product_id"]] = (a["category"], a["benefit"])
    return {k: v[0] for k, v in top.items()}

def transition_cost(current, candidate, cur_alloc, cand_alloc):
    cur_ids, cand_ids = {c["card_product_id"] for c in current}, {c["card_product_id"] for c in candidate}
    added, removed = cand_ids - cur_ids, cur_ids - cand_ids
    fee_delta = round((sum(c["annual_fee"] for c in candidate)
                       - sum(c["annual_fee"] for c in current)) / 12)
    rebuild = COST_REBUILD * len(added)
    cur_top, cand_top = primary_cats(cur_alloc), primary_cats(cand_alloc)
    role_changes = sum(1 for cid in (cur_ids & cand_ids)
                       if cur_top.get(cid) != cand_top.get(cid))
    items = len(added) + len(removed) + role_changes
    execution = round(COST_EXEC * items / 12)
    return dict(annual_fee_delta=fee_delta, performance_rebuild=rebuild,
                execution_burden=execution, total=fee_delta + rebuild + execution,
                added=sorted(added), removed=sorted(removed), role_changes=role_changes)

def new_card_pool(spend, held_ids, con):
    if not con["allow_new"]:
        return []
    top3 = [c for c, _ in sorted(spend.items(), key=lambda kv: (-kv[1], kv[0]))[:3]]
    scored = []
    for p in CATALOG:
        if p["card_product_id"] in held_ids or p["annual_fee"] > con["annual_fee_cap"]:
            continue
        best_rates = {}
        for t in p["tiers"]:
            for k, v in t["rates"].items():
                best_rates[k] = max(best_rates.get(k, 0), v)
        score = sum(spend[c] * best_rates.get(c, 0) for c in top3)
        scored.append(((-score, p["annual_fee"], p["card_product_id"]), p))
    scored.sort(key=lambda x: x[0])
    return [p for _, p in scored[:NEW_POOL]]

def run(persona, scenario="AS_EXPECTED"):
    coef = SCENARIOS[scenario]
    spend = {k: round(v * coef) for k, v in persona["spend"].items()}
    con = persona["constraints"]
    held = [BY_ID[i] for i in persona["held"]]
    current = held                                            # 최근 3개월 사용 이력 있는 카드 전부
    cur_gross, cur_alloc, _ = evaluate(current, spend)

    pool = sorted(held, key=lambda c: -sum(persona["spend"].values()))[:CUT_HELD]
    news = new_card_pool(spend, set(persona["held"]), con)
    combos = []
    for r in range(1, len(pool) + 1):
        for sub in itertools.combinations(pool, r):
            combos.append(list(sub))
            for n in news:
                combos.append(list(sub) + [n])
    for n in news:
        combos.append([n])

    scored = []
    for combo in combos:
        if len(combo) > con["max_cards"]:
            continue
        if sum(c["annual_fee"] for c in combo) > con["annual_fee_cap"]:
            continue
        g, alloc, _ = evaluate(combo, spend)
        tc = transition_cost(current, combo, cur_alloc, alloc)
        net = g - tc["total"]
        delta = net - cur_gross
        scored.append(dict(cards=[c["card_product_id"] for c in combo], gross=g,
                           transition_cost=tc, net_benefit=net, delta_net=delta,
                           allocation=alloc))
    scored.sort(key=lambda s: (-s["delta_net"], s["transition_cost"]["total"],
                               len(s["cards"]), sum(BY_ID[i]["annual_fee"] for i in s["cards"]),
                               s["cards"]))
    scored = scored[:MAX_CANDIDATES]

    passed = [s for s in scored
              if s["delta_net"] >= ABS_TH
              and (cur_gross == 0 or s["delta_net"] / cur_gross >= REL_TH)]
    best = passed[0] if passed else None
    return dict(scenario=scenario, spend=spend, current_cards=persona["held"],
                current_gross=cur_gross, candidate_count=len(scored),
                gating="RECOMMEND_CHANGE" if best else "KEEP_CURRENT",
                selected=best, top_candidates=scored[:3],
                current_allocation=cur_alloc)

# ══════════════════════════════════════════════════════════════════
# 픽스처 산출물
# ══════════════════════════════════════════════════════════════════
def mydata_snapshot(persona, rnd):
    """최근 3개월 거래 내역 — 월 지출 프로필을 건별로 쪼갠다."""
    txs = []
    for m in (3, 2, 1):
        base = DEMO_NOW.replace(day=1) - datetime.timedelta(days=1)
        month_end = base
        for _ in range(m - 1):
            month_end = month_end.replace(day=1) - datetime.timedelta(days=1)
        y, mo = month_end.year, month_end.month
        for cat, amt in persona["spend"].items():
            n = max(1, min(12, amt // 45000))
            weights = [rnd.uniform(.6, 1.4) for _ in range(n)]
            tot = sum(weights)
            parts = [int(amt * w / tot // 10) * 10 for w in weights]
            parts[-1] += amt - sum(parts)
            for p in parts:
                day = rnd.randint(1, 28)
                txs.append(dict(
                    tx_id=f"{persona['persona_id']}-{y}{mo:02d}-{len(txs)+1:04d}",
                    merchant=rnd.choice(MERCHANTS[cat]), category=cat,
                    category_label=CATEGORIES[cat], amount=p,
                    paid_at=f"{y}-{mo:02d}-{day:02d}",
                    card_product_id=rnd.choice(persona["held"])))
    txs.sort(key=lambda t: (t["paid_at"], t["tx_id"]))
    return txs

def terms_text(p):
    tiers = " / ".join(
        f"{t['min_spend']:,}원 이상 시 통합 월 {t['monthly_cap']:,}원 한도"
        for t in p["tiers"] if t["monthly_cap"] > 0)
    rates = ", ".join(
        f"{CATEGORIES[k]} {int(v*100)}%" for k, v in p["tiers"][-1]["rates"].items())
    exc = ", ".join(CATEGORIES[e] for e in p["exclusions"]) or "없음"
    return (f"[{p['issuer']} {p['name']} 이용약관 발췌 — 시연용 가공 문서]\n"
            f"제3조(전월 이용실적) 전월 이용실적 구간에 따라 혜택이 차등 적용된다. {tiers}.\n"
            f"제4조(할인율) 최고 구간 기준 {rates}.\n"
            f"제5조(제외 대상) 다음 이용금액은 이용실적 산정과 할인 적용에서 모두 제외한다: {exc}.\n"
            f"제6조(연회비) 국내전용 기준 연 {p['annual_fee']:,}원.\n"
            f"부칙 본 약관은 2026년 8월 1일부터 시행한다. (rule_version: {p['rule_version']})")

def terms_summary(p):
    top = p["tiers"][-1]
    best = sorted(top["rates"].items(), key=lambda kv: -kv[1])[:3]
    parts = ", ".join(f"{CATEGORIES[k]} {int(v*100)}%" for k, v in best)
    exc = ", ".join(CATEGORIES[e] for e in p["exclusions"]) or "없음"
    return (f"{p['issuer']} {p['name']}은 전월 실적 {top['min_spend']:,}원을 넘기면 "
            f"{parts} 할인을 월 {top['monthly_cap']:,}원까지 받는다. "
            f"제외 대상은 {exc}이며 연회비는 {p['annual_fee']:,}원이다.")

def explanation(persona, res):
    """AI 근거 설명 캐시 — 금액은 규칙 엔진 산출값을 그대로 인용한다(ADR-02)."""
    if res["gating"] == "KEEP_CURRENT":
        top = res["top_candidates"][0] if res["top_candidates"] else None
        head = (f"지금 쓰고 계신 조합이 이미 {persona['name']}님의 지출 구조에 맞습니다. ")
        if top and top["delta_net"] >= ABS_TH:
            ratio = top["delta_net"] / res["current_gross"] if res["current_gross"] else 0
            return (head + f"가장 나은 대안으로 바꾸면 월 {top['delta_net']:,}원이 늘지만, "
                    f"지금 혜택({res['current_gross']:,}원) 대비 {ratio:.1%}라 "
                    f"바꿀 만한 차이로 보기 어렵습니다. 그대로 두시면 됩니다.")
        return (head + "다른 조합으로 바꿔도 월 혜택이 크게 늘지 않고, 카드를 바꾸는 데 드는 "
                "부담을 빼면 오히려 손해입니다. 그대로 두시면 됩니다.")
    s = res["selected"]
    tc = s["transition_cost"]
    if tc["total"] < 0:
        cost = (f"연회비가 줄어 전환 부담이 오히려 월 {abs(tc['total']):,}원 이득입니다. ")
    else:
        cost = (f"카드를 바꾸는 데 드는 부담을 월 {tc['total']:,}원으로 잡아 뺐습니다. ")
    return (f"제안드린 조합은 월 {s['gross']:,}원의 혜택이 예상됩니다. " + cost +
            f"지금보다 월 {s['delta_net']:,}원이 늘어납니다. "
            f"해지 {len(tc['removed'])}장 · 새로 쓰기 시작하는 카드 {len(tc['added'])}장이며, "
            f"신청과 해지는 카드사에서 직접 진행하셔야 합니다.")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-o", "--out", default="tools/fixtures")
    a = ap.parse_args()
    out = pathlib.Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    rnd = random.Random(SEED)

    meta = dict(spec="FXT-CARDFIT-001", version=SPEC_VERSION, rule_spec=RULE_SPEC,
                demo_now=DEMO_NOW.isoformat(), seed=SEED,
                params=dict(abs_threshold=ABS_TH, rel_threshold=REL_TH,
                            scenario_delta=DELTA, cost_rebuild=COST_REBUILD,
                            cost_execution=COST_EXEC, max_candidates=MAX_CANDIDATES,
                            held_cut=CUT_HELD, new_pool=NEW_POOL))

    # ① 카드 상품 카탈로그 + ② 약관 원문·요약
    catalog = dict(**meta, total=len(CATALOG), issuers=ISSUERS, categories=CATEGORIES,
                   products=CATALOG)
    terms = dict(**meta, total=len(CATALOG),
                 documents=[dict(card_product_id=p["card_product_id"],
                                 rule_version=p["rule_version"],
                                 collected_at=DEMO_NOW.isoformat(),
                                 text=terms_text(p), ai_summary=terms_summary(p))
                            for p in CATALOG])

    # ③ 페르소나 + ④ 마이데이터 스냅샷 + ⑤ 계산 결과 기대값 + ⑥ AI 설명
    personas, snapshots, expected, explains = [], [], [], []
    mismatch = []
    for ps in PERSONAS:
        personas.append({k: v for k, v in ps.items() if k != "spend"} |
                        dict(future_spend_plan=ps["spend"],
                             plan_period_months=1))
        snapshots.append(dict(persona_id=ps["persona_id"],
                              as_of=DEMO_NOW.isoformat(),
                              consent_status=ps["consent"],
                              held_cards=[dict(card_product_id=i,
                                               issued_at="2024-03-11",
                                               used_last_3m=True) for i in ps["held"]],
                              transactions=mydata_snapshot(ps, rnd)))
        if ps["expect"] == "EXCEPTION":
            expected.append(dict(persona_id=ps["persona_id"], expect="EXCEPTION",
                                 note=ps["note"], scenarios=None))
            explains.append(dict(persona_id=ps["persona_id"], scenario=None,
                                 text="예외 경로 — AI 설명을 생성하지 않는다(응답 거부)."))
            continue
        per_scn = {}
        for scn in SCENARIOS:
            r = run(ps, scn)
            per_scn[scn] = dict(gating=r["gating"], current_gross=r["current_gross"],
                                candidate_count=r["candidate_count"],
                                selected=(None if not r["selected"] else dict(
                                    cards=r["selected"]["cards"],
                                    gross=r["selected"]["gross"],
                                    transition_cost=r["selected"]["transition_cost"],
                                    net_benefit=r["selected"]["net_benefit"],
                                    delta_net=r["selected"]["delta_net"],
                                    allocation=r["selected"]["allocation"])),
                                current_allocation=r["current_allocation"])
            if scn == "AS_EXPECTED":
                if r["gating"] != ps["expect"]:
                    mismatch.append((ps["persona_id"], ps["expect"], r["gating"]))
                explains.append(dict(persona_id=ps["persona_id"], scenario=scn,
                                     text=explanation(ps, r)))
        expected.append(dict(persona_id=ps["persona_id"], expect=ps["expect"],
                             note=ps["note"], scenarios=per_scn))

    # ⑦ 완주 계측·만료 시드 — 데모 클럭 기준 (FXT 6장)
    d30 = (DEMO_NOW - datetime.timedelta(days=30)).isoformat()
    d45 = (DEMO_NOW - datetime.timedelta(days=45)).isoformat()
    outcome_seeds = []
    for e in expected:
        if not e["scenarios"]:
            continue
        scn = e["scenarios"]["AS_EXPECTED"]
        if scn["gating"] != "RECOMMEND_CHANGE":
            continue
        outcome_seeds.append(dict(
            persona_id=e["persona_id"], selected_scenario="AS_EXPECTED",
            selected_cards=scn["selected"]["cards"], selected_at=d30,
            status="NOT_SENT", due_at=DEMO_NOW.isoformat(),
            note="선택 +30일 도달 — 발송 대상으로 즉시 조회된다 (REQ-FUNC-010)"))
    expiry_seeds = [
        dict(persona_id="P4", base_date=d45, reason="BASE_DATE_PLUS_30",
             note="기준일 +30일 경과 만료 (REQ-EXC-006)"),
        dict(persona_id="P3", base_date=d30, reason="RULE_VERSION_CHANGED",
             changed_card="LTC-ONLINE", new_rule_version="2026-08-20-ltc-online",
             note="rule_version 변경 만료 (ADR-06 · REQ-NF-007)"),
    ]

    files = {
        "card-products.json": catalog,
        "terms.json": terms,
        "personas.json": dict(**meta, total=len(personas), personas=personas),
        "mydata-snapshots.json": dict(**meta, total=len(snapshots), snapshots=snapshots),
        "expected-results.json": dict(**meta, total=len(expected), results=expected),
        "ai-cache.json": dict(**meta, total=len(explains) + len(CATALOG),
                              explanations=explains,
                              term_summaries=[dict(card_product_id=p["card_product_id"],
                                                   rule_version=p["rule_version"],
                                                   summary=terms_summary(p))
                                              for p in CATALOG]),
        "demo-clock.json": dict(**meta, outcome_seeds=outcome_seeds,
                                expiry_seeds=expiry_seeds,
                                total=len(outcome_seeds) + len(expiry_seeds)),
    }
    for name, doc in files.items():
        (out / name).write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")

    tx = sum(len(s["transactions"]) for s in snapshots)
    print(f"생성 → {out}/")
    print(f"  카드 상품 {len(CATALOG)}종 (카드사 {len(ISSUERS)}곳) · 약관 {len(CATALOG)}건")
    print(f"  페르소나 {len(personas)}인 · 거래 {tx}건 · AI 설명 {len(explains)}건")
    print(f"  완주 계측 시드 {len(outcome_seeds)}건 · 만료 시드 {len(expiry_seeds)}건")
    for e in expected:
        if e["scenarios"] is None:
            print(f"  {e['persona_id']}: EXCEPTION (예외 전용)")
            continue
        g = {s: v["gating"] for s, v in e["scenarios"].items()}
        print(f"  {e['persona_id']}: 기대 {e['expect']} · 실측 {g['AS_EXPECTED']} "
              f"(적게 {g['LESS']} / 많이 {g['MORE']})")
    if mismatch:
        print("\n❌ 기대 결론 불일치:", mismatch)
        raise SystemExit(1)
    print("\n✅ 페르소나 전건이 의도한 결론을 낸다 (예상대로 시나리오 기준)")

if __name__ == "__main__":
    main()
