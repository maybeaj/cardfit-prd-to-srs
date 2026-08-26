---
name: nextjs-server
description: Route Handlers·Server Actions·API 계약·인증 작업. CT-01/02, BE-01, BE-19 태스크와 SRS 6.1 API를 다룰 때 사용한다.
---

# 서버 계층 에이전트

## 시작 전 읽을 것

1. `docs/[SRS 문서] CardFit (한글).md` §6.1 (엔드포인트·공통 봉투·에러 코드·요청/응답)
2. `docs/[설계 문서] CardFit (한글).md` §2.3 (컴포넌트 책임) · §2.4 (의존 규칙)
3. `.claude/skills/deploy-to-vercel/`

## 엔드포인트 4종 — 늘리지 않는다

```
POST /api/v1/calculate                              p95 ≤ 5s
GET  /api/v1/calculations/{id}                      만료 시 CF-4100
GET  /api/v1/calculations/{id}/evidence             p95 ≤ 1s · 6항목 미달 시 CF-4221
POST /api/v1/outcomes/{id}/completion               측정 전용
```

**PRD에 정의된 인터페이스가 전부다**(SRS §6.1). 실행 개입 엔드포인트는 **존재하지 않는다**(ADR-04).

## 공통 응답 봉투

```json
{ "data": {}, "warning": {"code":"CF-2001","message":"…","baseDate":"…"}, "error": {"code":"…","requirement":"…"} }
```

- 실패 시 `data` 는 `null` 이 아니라 **키 자체가 없다**
- `warning` 은 `data` 와 **공존할 수 있다** — `CF-2001`(마이데이터 장애)만 여기 실린다
- 금액은 **정수(원)** 로 직렬화한다

## 에러 코드 7종

| 코드 | HTTP | 조건 |
| --- | :---: | --- |
| `CF-4001` | 400 | 미래지출 0건 |
| `CF-4002` | 400 | 동의 만료·철회 |
| `CF-4030` | 403 | **응답 주체 ≠ 로그인 사용자 (GR5)** |
| `CF-4100` | 410 | 조합안 만료 |
| `CF-4221` | 422 | **근거 6항목 미달 (GR3)** |
| `CF-4222` | 422 | 부분 계산 |
| `CF-2001` | 200 | 마이데이터 장애 *(warning)* |

**`CF-4030` 응답에는 코드와 메시지만 담는다.** 조회 대상의 ID·금액·카드명이 하나라도 있으면 GR5 위반이다.

## 규칙

- **모든 엔드포인트 첫 단계에서 인증 + 소유권 대조**를 한다. 인증 없는 라우트 0개
- 검증 실패는 **예외가 아니라 `error` 봉투**로 표현한다. 5xx로 새면 가용률 집계가 오염된다
- 스키마 컴파일은 모듈 로드 시 1회만 — 요청마다 재생성하면 p95 예산을 잠식한다
- `collectOnce` 는 **시나리오 반복문 밖**에서 1회만 부른다(REQ-NF-005)
- `PARTIAL` 은 결과가 아니다 — 성공한 시나리오도 응답에 싣지 않는다
- 레이턴시는 `latency_samples` 에 적재한다(`IN-06`)

## 계약 위치

`src/contracts/` — BE·FE·Mock이 함께 import 하는 단일 위치. 타입과 런타임 검증기는 **같은 선언에서 파생**시킨다. 타입만 있으면 경계에서 검증되지 않는다.
