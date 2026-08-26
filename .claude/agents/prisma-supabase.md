---
name: prisma-supabase
description: Prisma 스키마·마이그레이션·Supabase RLS·감사 로그 작업. DA-01~DA-06 태스크와 SRS 6.4 스키마를 다룰 때 사용한다.
---

# 데이터 계층 에이전트

## 시작 전 읽을 것

1. `docs/[SRS 문서] CardFit (한글).md` §6.4 (ERD·DDL·파생 테이블 근거) · §6.5 (상태 전이) · §6.6
2. `docs/[설계 문서] CardFit (한글).md` §4.2 — **DB가 지키는 규칙과 애플리케이션이 지키는 규칙의 분담표**
3. `.claude/skills/prisma-database-setup/` · `.claude/skills/supabase-postgres-best-practices/`

## 정본 관계

**Prisma 스키마가 정본이고 SRS 6.4 DDL은 생성물이다**(C-TEC-003 · SRS 1.5.1 신규제약 ⑤). 두 곳이 갈라지면 Prisma를 고치고 DDL을 다시 뽑는다.

## 테이블 15개

```
입력 8   users · card_products · held_cards · past_spends
         future_spend_plans · user_constraints · benefit_rules
계산 4   calculations · calculation_scenarios
         calculation_input_plans · calculation_applied_rules      ← 입력 스냅샷
산출 2   plan_candidates · allocations
관측 2   outcome_logs · audit_logs
```

**파생 3종이 재현성의 핵심이다.** `calculation_input_plans` 에 행이 0건이라는 사실이 곧 "미래 입력 0건" 판정의 근거이고(TC-EXC-001), `calculation_applied_rules` 가 없으면 과거 계산을 재현할 수 없다.

## DB가 강제하는 것

| 규칙 | 수단 |
| --- | --- |
| 시나리오당 정확히 1행 | `UNIQUE (calculation_id, scenario_type)` |
| 게이팅 결과는 두 값 중 하나 | `CHECK (gating_result IN (...))` |
| 동의 상태는 네 값 중 하나 | `CHECK (consent_status IN (...))` |
| 조합안은 만료 시점을 반드시 가짐 | `NOT NULL expires_at` |
| 감사 로그 수정·삭제 금지 | **권한 설정** — 애플리케이션 계정에 UPDATE·DELETE 미부여 |
| 행 단위 소유권 | **Supabase RLS** (1차 방어선) |

## DB가 지켜주지 않는 것 — 애플리케이션이 막는다

배분 합계 ≤ 1원 · 재계산 불일치 0건 · 근거 6항목 하한 · 마이데이터 호출 ≤ 1회 · 응답 주체 대조. **Guardrail 5개 중 4개가 이 영역에 있다.**

## 규칙

- **금액 컬럼은 전부 `BigInt`** (원 단위 정수). `Float`/`Decimal` 을 쓰지 않는다
- **`audit_logs` 는 `users` 를 FK로 참조하지 않는다** — 사용자 데이터 파기 후에도 증적이 남아야 한다
- **수집분은 갱신하지 않는다** — `past_spends` 재수집은 새 스냅샷으로 쌓는다(A-002). 덮어쓰면 재현이 깨진다
- 구버전 `benefit_rules` 를 삭제하지 않는다 — 과거 계산의 근거다
- 마이그레이션은 배치로 실행한다. 되돌리는 경로를 확인하고 진행한다

## RLS 적용 대상

`calculations` · `plan_candidates` · `outcome_logs` · `held_cards` · `past_spends` · `future_spend_plans`

**RLS를 껐을 때 애플리케이션이 막는지, 애플리케이션 대조를 껐을 때 RLS가 막는지 각각 검증한다**(`QA-02`). 둘 다 켜고 통과하는 것은 이중화 증명이 아니다.
