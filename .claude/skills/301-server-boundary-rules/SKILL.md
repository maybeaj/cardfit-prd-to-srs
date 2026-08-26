---
name: 301-server-boundary-rules
description: 서버 코드를 어디에 놓고 무엇을 호출할 수 있는지 정한다. 새 모듈 생성, import 추가, Route Handler·Server Action 작성 전에 확인한다. ADR-02 경계 위반은 빌드가 아니라 린트가 잡는다.
---

# 서버 경계 규칙

## 디렉터리 경계

```
src/
  contracts/        BE·FE·Mock이 함께 import 하는 단일 계약 위치
  domain/
    calc/           결정론 영역 — AI가 import 할 수 없다
    ai/             ExplanationModule — 계산 결과를 인자로만 받는다
  data/             Prisma · 외부 어댑터
  app/              App Router (Route Handlers · Server Actions)
```

**단일 Next.js 앱이라 계층을 물리적으로 분리할 수 없다**(SRS 1.5.1 신규제약 ①). `import` 한 줄이면 경계를 넘고, 넘어도 빌드가 깨지지 않는다. 그래서 **의존성 경계 린트(`IN-04`)가 유일한 강제 장치**다.

## 금지 방향 4가지

| # | 금지 | 근거 |
| :---: | --- | :---: |
| 1 | `domain/ai/**` → `domain/calc/**` | **ADR-02** — AI는 계산을 호출할 수 없다 |
| 2 | `data/**` → `domain/**` 응용 계층 | SDD §2.4 규칙 1 (아래 계층만 호출) |
| 3 | `MyDataConnector` 외 → 마이데이터 어댑터 직접 import | REQ-NF-005 호출 계수의 전제 |
| 4 | 감사 로그 모듈에 UPDATE·DELETE 경로 | REQ-NF-006 append-only |

**경계 규칙에 인라인 예외(`eslint-disable`)를 두지 않는다.** 예외를 허용하면 경계가 사실상 사라진다.

## 서버 진입점

| 종류 | 언제 | 규칙 |
| --- | --- | --- |
| Route Handler | 외부에 노출되는 API 4종 | 인증 + 소유권 대조가 **첫 단계** |
| Server Action | 폼 제출·내부 변이 | 공개 엔드포인트와 동등하게 취급 — 인가를 첫 줄에서 확인 |

**엔드포인트를 늘리지 않는다.** SRS §6.1이 정의한 4종이 전부이며, 실행 개입 엔드포인트는 존재하지 않는다(ADR-04).

## 모듈 간 호출

**내부 모듈을 HTTP로 부르지 않는다.** 같은 프로세스이므로 함수로 호출한다. REST로 나누면 C-TEC-001의 단일 앱 전제가 깨지고 레이턴시 예산도 잠식된다.

## 외부 호출은 한 곳에서

| 외부 | 유일한 통로 |
| --- | --- |
| 마이데이터 | `MyDataConnector` → `MyDataProvider` (fixture / live) |
| AI | `ExplanationModule` → `AiOutputProvider` (cache / live) |
| DB | `data/` 계층의 Prisma 클라이언트 |

**호출을 한 곳에서 세지 못하면 예산을 보증할 수 없다** — 결론 1건당 마이데이터 ≤ 1회(REQ-NF-005), 근거 설명 1건당 AI ≤ 1회.
