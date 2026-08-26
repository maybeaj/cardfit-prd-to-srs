---
name: fixture-mode
description: 픽스처 어댑터 경계·시드 적재·캐시↔실호출 전환 작업. IN-08, DA-05, DA-06, BE-14, BE-20, BE-03 태스크를 다룰 때 사용한다.
---

# 픽스처 모드 에이전트

## 왜 있나

마이데이터 인가·카드사 범위·외부 AI 전송이 규제·계약 결정을 기다리는 항목이라, **그것을 기다리지 않고 개발·시연이 가능하도록** 외부 경계를 사전 생성 데이터로 대체했다. SRS 10.3의 D1·D4·D11·D13·D14가 이렇게 처리됐다.

## 시작 전 읽을 것

`docs/tech-design-docs/[FXT]cardfit-fixture-spec.md` — 특히 **1장(모드 경계)** 과 **9장(대체하지 못하는 것)**

## 대체하는 것과 대체하지 않는 것

| 계층 | fixture | live |
| --- | --- | --- |
| 마이데이터 수집 | `FixtureMyDataProvider` | `ApiMyDataProvider` |
| 카드 상품·약관 | 카탈로그 24종 시드 | 수집 배치 |
| AI 요약·설명 | 캐시 조회 | Vercel AI SDK 호출 |
| 발송·알림·분석·APM | 테이블 4종 적재 | 외부 도구 |
| **계산·게이팅·근거 게이트** | **대체하지 않는다** | 동일 |
| **인증·RLS·감사** | **대체하지 않는다** | 동일 |

> **픽스처가 계산 결과를 들고 있으면 제품이 아니라 픽스처를 검증한 것이 된다.** 대체는 외부 경계에서 멈춘다.

## 전환 규칙

- `CARDFIT_DATA_MODE=fixture | live` 하나로 고른다
- **두 구현이 같은 인터페이스를 만족**해야 한다 (타입 수준 검증)
- **캐시 미스가 실호출로 새지 않는다** — fixture 모드에서 캐시가 없으면 `null` 을 반환한다. 조용한 폴백은 "외부 호출 0회" 보증을 깨뜨린다
- 프로바이더 호출은 한 곳에서만 — `MyDataConnector` 외 모듈이 어댑터를 직접 import 하면 린트가 막는다(REQ-NF-005 계수의 전제)

## 시드 데이터

```
tools/fixtures/card-products.json      상품 24종 (카드사 8곳)
tools/fixtures/terms.json              약관 원문 + 요약 24건
tools/fixtures/personas.json           페르소나 5인
tools/fixtures/mydata-snapshots.json   거래 348건
tools/fixtures/expected-results.json   기대 결론 (참조 계산기 산출)
tools/fixtures/ai-cache.json           근거 설명 5 + 약관 요약 24
tools/fixtures/demo-clock.json         완주 시드 2 + 만료 시드 2
```

**고정 시드(`SEED=20260825`)라 실행마다 같은 결과가 나온다.** 재생성은 `python3 tools/generate_fixtures.py`.

## 페르소나 5인

| ID | 결론 | 무엇을 시연하나 |
| :---: | :---: | --- |
| P1 | KEEP | 절대 기준부터 미달인 명백한 유지 |
| P2 | KEEP | **절대 통과·상대 미달** — GR2 경계의 시험대 |
| P3 | CHANGE | **전환비용이 음수** (연회비 절감) |
| P4 | CHANGE | 신규 발급 포함 · 북극성 경로 |
| P5 | 예외 | 동의 만료 · 수집 장애 · 근거 미달 |

## 데모 클럭

**계산·판정 경로에서 `now()` 를 직접 호출하지 않고 주입받는다.** 30일 대기와 만료를 기다리지 않고 재현하기 위해서이자, 결정론(REQ-NF-002)의 전제이기도 하다.

## 반드시 함께 남길 것

`mode:fixture` 태스크를 구현할 때는 **실서비스 전환 시 무엇이 다시 열리는지**를 코드 주석과 이슈 본문에 남긴다. D1·D4·D9·D11·D13 중 어느 것인지 명시한다.

## 화면 요구

**모든 화면에 "시연용 가공 데이터" 배지를 노출한다.** 실제 카드사명을 쓰므로 이 배지가 없으면 혜택 정보를 사실로 오인한다(FXT 2.1절).
