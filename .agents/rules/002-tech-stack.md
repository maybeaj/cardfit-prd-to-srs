---
description: CardFit 기술 스택 — SRS 1.5 C-TEC 제약
alwaysApply: true
---
# Technical Stack

**아래는 선택지가 아니라 제약이다.** SRS 1.5가 고정했고, 바꾸려면 SRS를 먼저 고쳐야 한다.

## Core

| 영역 | 값 | 제약 ID |
| --- | --- | :---: |
| 프레임워크 | Next.js **App Router** (Pages Router 사용 안 함) | C-TEC-001 |
| 언어 | TypeScript **strict** | — |
| 서버 로직 | Server Actions / Route Handlers | C-TEC-002 |
| DB | Supabase (PostgreSQL) | C-TEC-003 |
| ORM | **Prisma** — 스키마가 정본, SRS 6.4 DDL은 생성물 | C-TEC-003 |
| UI | Tailwind CSS + **shadcn/ui** | C-TEC-004 |
| AI | **Vercel AI SDK** — 자체 서버 없이 외부 API 호출 | C-TEC-005 |
| LLM | Google Gemini 기본, **환경변수만으로 교체** | C-TEC-006 |
| 배포 | **Vercel** — Git Push 자동화, 파이프라인 미구성 | C-TEC-007 |
| 검증 게이트 | **1개만 허용** — 경계값 회귀 + 금지어 스캔 | C-TEC-007a |

## 디렉터리 경계

**ADR-02를 디렉터리로 드러낸다.** 의존성 경계 린트(`IN-04`)의 검사 단위다.

```
src/
  contracts/        # BE·FE·Mock이 함께 import 하는 단일 계약 위치
  domain/
    calc/           # 결정론 영역 — AI가 import 할 수 없다
    ai/             # ExplanationModule — 계산 결과를 인자로만 받는다
  data/             # Prisma · 어댑터
  app/              # App Router
```

## 환경변수

| 변수 | 값 | 용도 |
| --- | --- | --- |
| `DATABASE_URL` | Supabase 연결 문자열 | Prisma |
| `CARDFIT_DATA_MODE` | `fixture` \| `live` | 마이데이터·AI 어댑터 전환 |
| AI 모델 식별자 | Gemini 기본 | **변경 시 배포 게이트 ② 재실행** |

**환경변수 없이 기동하면 명시적 오류로 실패한다.** 조용히 기본값으로 뜨면 어떤 모드로 도는지 아무도 모른다.

## 스택에 없어서 직접 만든 것 (D14)

발송·알림·분석·APM 도구를 도입하지 않고 테이블 4종으로 대체했다.

| 수단 | 구현 |
| --- | --- |
| 사용자 발송 | `outbox` |
| 실시간 알림 | `alerts` |
| 이벤트 분석 | `events` (7종) |
| APM | `latency_samples` |

## 외부 레퍼런스

`.claude/skills/` 에 Prisma·Supabase·Vercel 공식 스킬을 두었다. 채택 근거는 `docs/[하네스 구성] CardFit (한글).md`.
