---
description: 태스크 이슈 하나를 착수 조건 점검부터 시작한다
argument-hint: [태스크 ID 또는 이슈 번호 — 예 BE-06 또는 37]
allowed-tools: Read, Grep, Glob, Bash, Edit, Write
---

# 태스크 착수

대상: **$ARGUMENTS**

## Step 1. 태스크 식별

- `tools/issue-map.json` 에서 태스크 ID ↔ 이슈 번호를 확인한다
- `docs/tasks/<ID>.md` 를 읽는다

## Step 2. 착수 조건 (Definition of Ready)

아래를 확인하고 하나라도 아니면 **작업을 시작하지 않고 보고한다.**

- [ ] `Depends on` 의 선행 태스크가 전건 완료됐는가? (`gh issue view <번호> --json state`)
- [ ] References의 문서를 읽었는가?
- [ ] `mode:fixture` 라벨이면 External Blocker 재개 조건을 이해했는가?

## Step 3. 근거 문서 읽기

태스크 성격별로 **반드시 먼저 읽을 것**을 정한다.

| 성격 | 문서 |
| --- | --- |
| 계산·게이팅·조합·배분 | `docs/[계산 명세서] CardFit (한글).md` — **값의 정본** |
| 픽스처·어댑터·시드 | `docs/[픽스처 데이터 명세] CardFit (한글).md` |
| API·스키마·에러 코드 | `docs/[SRS 문서] CardFit (한글).md` §6 |
| 화면 | 대응 `DS-0N` 설계 태스크 |
| 테스트 | `docs/[테스트 명세서] CardFit (한글).md` — **AC를 새로 만들지 않는다** |

## Step 4. 서브에이전트 선택

| 태스크 | 에이전트 |
| --- | --- |
| CT · BE-01 · BE-19 | `nextjs-server` |
| DA-01~04 | `prisma-supabase` |
| BE-06~12 · BE-16 | `calc-engine` |
| IN-08 · DA-05·06 · BE-14·20 · BE-03 | `fixture-mode` |
| BE-18 · IN-03 · QA-01 | `compliance-guardrail` |
| FE · DS | `frontend-shadcn` |

## Step 5. 계획 제시

Task Breakdown 체크리스트를 **그대로** 실행 계획으로 쓴다. 항목을 임의로 늘리거나 줄이지 않는다. 늘려야 할 이유를 발견하면 **먼저 보고한다.**

## Step 6. 구현

- 불변식 6(`​.agents/rules/004-invariants.md`)을 어기지 않는다
- 계산 도메인이면 결정론 체크리스트를 함께 통과시킨다

## Step 7. 완료 판정

공통 DoD 8항목 + 태스크별 추가 항목을 확인하고, **통과하지 못한 항목은 통과했다고 적지 않는다.**

```bash
python3 tools/verify_docs.py
python3 tools/generate_fixtures.py    # 계산 도메인일 때
```
