---
name: 302-data-access-rules
description: Prisma 스키마·마이그레이션·쿼리와 Supabase RLS·감사 로그 규칙. 테이블을 만들거나 바꿀 때, 쿼리를 쓸 때, 금액 컬럼을 다룰 때 확인한다.
---

# 데이터 접근 규칙

**Prisma 스키마가 정본이다.** SRS 6.4의 DDL은 생성물이며, 두 곳이 갈라지면 Prisma를 고치고 DDL을 다시 뽑는다(C-TEC-003 · SRS 1.5.1 신규제약 ⑤).

## 금액 — 예외 없다

- 컬럼 타입은 **`BigInt`**(원 단위 정수). `Float`·`Decimal`·`Double` 을 쓰지 않는다
- JSON 직렬화도 정수
- 반올림은 계산 명세 2.6절이 정본 — 카테고리 혜택은 **내림**, 월 환산은 **반올림**
- 배분 잔여 오차는 배분 금액 최대 카테고리에 흡수 (합계 오차 ≤ 1원)

> 부동소수 하나가 GR1(계산 오류율)과 REQ-FUNC-005(배분 합계)를 동시에 깨뜨린다.

## DB가 강제하는 것 — 애플리케이션에 맡기지 않는다

| 규칙 | 수단 |
| --- | --- |
| 시나리오당 정확히 1행 | `UNIQUE (calculation_id, scenario_type)` |
| 게이팅 결과는 두 값 중 하나 | `CHECK` |
| 동의 상태는 네 값 중 하나 | `CHECK` |
| 조합안은 만료 시점을 반드시 가짐 | `NOT NULL expires_at` |
| 행 단위 소유권 | **Supabase RLS** (1차 방어선) |
| 감사 로그 수정·삭제 금지 | **권한 설정** — 애플리케이션 계정에 UPDATE·DELETE 미부여 |

## DB가 지켜주지 않는 것 — 코드가 유일한 방어선

배분 합계 ≤ 1원 · 재계산 불일치 0건 · 근거 6항목 하한 · 마이데이터 호출 ≤ 1회 · 응답 주체 대조.

**Guardrail 5개 중 4개가 이 영역에 있다**(SDD §4.2).

## 보존과 파기

- **`audit_logs` 는 `users` 를 FK로 참조하지 않는다** — 사용자 데이터 파기 후에도 증적이 남아야 한다
- **수집분은 갱신하지 않는다** — `past_spends` 재수집은 새 스냅샷으로 쌓는다(가정 A-002). 덮어쓰면 과거 계산 재현이 깨진다
- **구버전 `benefit_rules` 를 삭제하지 않는다** — 과거 계산의 근거다
- 동의 철회 시 수집 데이터는 **24시간 내** 파기하되 감사 로그는 남긴다

## RLS 적용 대상

`calculations` · `plan_candidates` · `outcome_logs` · `held_cards` · `past_spends` · `future_spend_plans`

**한쪽을 껐을 때 다른 쪽이 막는지 각각 검증한다**(`QA-02`). 둘 다 켜고 통과하는 것은 이중화 증명이 아니다.

## 마이그레이션

- 배치로 실행한다. 테이블 하나당 마이그레이션 하나는 실제 작업 단위보다 잘다
- 되돌리는 경로를 확인하고 진행한다
- 시드 순서는 **`DA-05`(상품·약관) → `DA-06`(페르소나·거래)** 다

## 참고 스킬

`prisma-client-api` · `prisma-database-setup` · `supabase-postgres-best-practices`
