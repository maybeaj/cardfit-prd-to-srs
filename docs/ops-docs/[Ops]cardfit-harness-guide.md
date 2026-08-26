# [Ops] CardFit (한글)

# 에이전트 규칙 세팅 — 채택·수정·삭제 근거

**문서 ID:** HRN-CARDFIT-001

**개정 버전:** 2.0

**날짜:** 2026-08-26

**참조 하네스:** `wild-mental/AI-multivender-harness-sample`

**외부 스킬 출처:** [skills.sh](https://www.skills.sh/) — `prisma/skills` · `supabase/agent-skills` · `vercel-labs/agent-skills` · `mattpocock/skills` · **`wild-mental/*-skill` 4종**

---

## 0. 이 문서가 남기는 것

**무엇을 가져왔고, 무엇을 고쳤고, 무엇을 버렸는지.** 규칙은 시간이 지나면 "왜 이렇게 돼 있지"가 되므로 판단의 근거를 함께 남긴다.

---

## 1. 참조 하네스를 그대로 쓸 수 없었던 이유

`AI-multivender-harness-sample`은 **Java/Spring + Python FastAPI + Kafka + Flutter** 스택을 전제로 만들어진 템플릿이다. CardFit은 SRS 1.5가 **Next.js 단일 풀스택**으로 고정했다.

| 참조 하네스 | CardFit | 결과 |
| --- | --- | :---: |
| Java 21 · Spring Boot 4 | **Next.js App Router · TypeScript** | 교체 |
| Gradle | npm | 삭제 |
| MySQL 8 + JPA/QueryDSL | **Supabase(PostgreSQL) + Prisma** | 교체 |
| Kafka (파이프라인 · Saga) | 없음 — 큐 없이 Vercel Cron | 삭제 |
| Redis (Lettuce/Redisson) | 없음 | 삭제 |
| Python FastAPI + LangChain | 없음 — Vercel AI SDK | 삭제 |
| React + Vite (SPA) | **Next.js + shadcn/ui** | 교체 |
| Flutter + Riverpod | 없음 (웹 확정) | 삭제 |
| Docker Compose | Vercel + 로컬 Supabase | 삭제 |
| Micro-Service Ready (REST 분리) | **단일 코드베이스**(C-TEC-001) | 교체 |

> **구조는 가져오고 내용은 전부 바꿨다.** `.agents/rules/` + `.claude/agents/` + `.claude/commands/` 3계층 분리와 "항상 적용은 규칙 파일, 도메인 지식은 서브에이전트, 절차는 커맨드"라는 배치 원칙은 그대로 쓸 만했다.

### 1.1 벤더 디렉터리를 정리했다

참조 하네스는 `.cursor/` · `.gemini/` 까지 갖춘 멀티벤더 구성이다. **같은 내용을 세 곳에서 관리하게 되므로 가져오지 않았다.**

| 항목 | 처리 |
| --- | --- |
| `.claude/` | **채택** — 이 프로젝트의 주 작업 환경 |
| `AGENTS.md` | **채택** — 벤더 중립 표준. 한 파일이면 유지 비용이 낮다 |
| `.agents/rules/` | **채택** — 벤더 중립 규칙 |
| `.cursor/` (rules · skills 20여 종) | **삭제** — 대부분 Java/Kafka/Flutter 전용이고, 남는 것도 `.claude/`와 중복 |
| `.gemini/` | **삭제** — 동일 |
| `README-*-harness.md` 4종 | **삭제** — 이 문서가 대신한다 |

---

## 2. 세팅한 구조

**v2.0에서 참조 프로젝트(`ai-place-mate-prd-to-srs`)와 배치를 맞췄다.** 같은 하네스에서 출발했지만 갈라져 있었다 — 참조는 절차·규칙을 **번호 붙은 스킬**로 `.agents/skills/`에 두고 `.claude/skills/`로 미러했고, 우리는 `.claude/commands/`(슬래시 커맨드) + `.claude/agents/`로 나눴었다.

```
CLAUDE.md                    Claude Code 자동 로드 — 스택 · 불변식 6 · 라우팅
AGENTS.md                    벤더 중립 규칙
skills-lock.json             외부 스킬 15종의 출처·경로·해시
.agents/
  rules/                     항상 적용 4종 (001~004)
  skills/                    ← 원본
    100-error-fixing-process · 101-build-and-env-setup
    200-git-commit-push-pr · 201-code-commenting · 202-github-issue-handling
    300-tech-constraints-guardrails · 301-server-boundary-rules
    302-data-access-rules · 303-ai-integration-rules · 304-calc-gating-rules
    400-task-execution-workflow · 401-verification-workflow
    + 외부 15종
.claude/
  skills/                    ← 위의 미러 (Claude Code 가 읽는 자리)
  agents/                    도메인별 6종
```

### 2.0 왜 커맨드를 스킬로 바꿨나

| 이유 | 설명 |
| --- | --- |
| **벤더 중립** | `.claude/commands/`는 Claude Code 전용이다. `.agents/skills/`에 두면 다른 도구도 읽는다 |
| **호출 방식** | 커맨드는 사람이 `/name`으로 부를 때만 뜬다. 스킬은 **설명이 맞으면 모델이 스스로 꺼내 읽는다** — 300번대 기술 규칙처럼 "코드 쓰기 전에 봐야 하는 것"에 적합하다 |
| **참조와 동일** | 같은 계보의 프로젝트가 같은 배치를 쓴다 |

**대신 미러 유지 비용이 생겼다.** `.agents/`를 고치면 `.claude/`도 함께 고쳐야 한다.

### 2.0.1 번호 체계

| 번호대 | 성격 | 우리 스킬 |
| :---: | --- | --- |
| 100 | 프로세스 | 에러 진단 · 환경 기동 |
| 200 | 협업 | 커밋·PR · 주석 · 이슈/프로젝트 |
| **300** | **기술 규칙** | 제약 가드레일 · 서버 경계 · 데이터 접근 · AI 통합 · **계산·게이팅** |
| 400 | 워크플로 | 태스크 실행 · 전체 검증 |

**304-calc-gating-rules 는 참조에 없는 우리 고유 항목이다.** 계산 결정론과 게이팅 두 조건이 이 제품의 중심이라 별도 번호를 뒀다.

### 2.1 신설한 것 — 불변식 4종

참조 하네스에 없던 계층이다. **이 프로젝트에서 어기면 서비스가 중단되는 규칙**을 한곳에 모았다.

| # | 불변식 | 대응 Guardrail |
| :---: | --- | :---: |
| I1 | AI는 계산 영역을 호출하지 않는다 (ADR-02) | — |
| I2 | 금액은 원 단위 정수 | GR1 |
| I3 | 계산 경로에 비결정론 금지 | GR1 |
| I4 | 임계 미달이면 변경 제안 금지 | **GR2** |
| I5 | 근거 6항목 미달 시 응답 거부 | **GR3** |
| I6 | 응답 주체 ≠ 로그인 사용자면 즉시 차단 | **GR5** |

**일반적인 "좋은 관행"은 규칙으로 쓰지 않았다.** "모듈화된 설계", "성능 최적화" 같은 문구는 어떤 코드도 막지 못한다. 대신 **위반을 판정할 수 있는 것**만 남겼다.

### 2.2 서브에이전트 — 스택 대응 3 + 신설 3

| 참조 하네스 | CardFit | 성격 |
| --- | --- | :---: |
| `java-spring` | **`nextjs-server`** | 대응 |
| `jpa-querydsl` | **`prisma-supabase`** | 대응 |
| `react-frontend` | **`frontend-shadcn`** | 대응 |
| `gradle` · `spring-redis` · `kafka-pipeline` · `kafka-saga` · `flutter-app` | — | **삭제** |
| — | **`calc-engine`** | **신설** — 이 제품의 핵심 도메인 |
| — | **`fixture-mode`** | **신설** — 어댑터 경계·시드·전환 |
| — | **`compliance-guardrail`** | **신설** — Guardrail 5건·배포 게이트 |

> **`calc-engine`이 가장 중요하다.** 계산 파이프라인 S1~S6, 게이팅 두 조건, 조합 정렬 5키, 결정론 체크리스트를 담았다. 이 프로젝트에서 가장 위험한 코드가 여기 있다.

### 2.3 커맨드 — 적응 3 + 신설 2

| 참조 하네스 | CardFit | 무엇을 고쳤나 |
| --- | --- | --- |
| `/fix-error` | **`/fix-error`** | **Step 0 신설** — 증상별로 어느 불변식을 먼저 의심할지 표를 넣었다 |
| `/setup-env` | **`/setup-env`** | Supabase·Prisma·픽스처 시드 순서로 교체 |
| `/gitflow-commit` | **`/gitflow-commit`** | 이 저장소의 커밋 관례(`type: 제목 — 부제` + ①②③)로 교체 |
| — | **`/task-start`** | **신설** — 이슈 하나를 DoR 점검부터 시작 |
| — | **`/verify`** | **신설** — 문서 110항목 · 픽스처 · 금지어 · 그래프를 한 번에 |

**참조 하네스의 `generate-tasks-from-srs` 워크플로는 가져오지 않았다.** 이미 태스크 59건이 추출돼 이슈로 발급된 상태라 쓸 자리가 없다.

---

## 3. 외부 스킬 채택 (skills.sh)

### 3.1 채택 8종

| 스킬 | 출처 | 왜 |
| --- | --- | --- |
| `prisma-client-api` | `prisma/skills` | Prisma가 ORM 정본(C-TEC-003). DA·BE 전 계층이 쓴다 |
| `prisma-database-setup` | `prisma/skills` | `IN-01` 초기화 · `DA-01~04` 마이그레이션 |
| `supabase-postgres-best-practices` | `supabase/agent-skills` | **`DA-04`의 RLS·append-only 근거.** 오조회 0건(GR5)의 1차 방어선 |
| `deploy-to-vercel` | `vercel-labs/agent-skills` | `IN-02`·`IN-03` — Git Push 배포와 게이트 |
| `vercel-react-best-practices` | `vercel-labs/agent-skills` | FE 8건. 설치 663K로 검증된 공식 레퍼런스 |
| `tdd` | `mattpocock/skills` | `TS-01~03`. STD가 GWT 기반이라 red-green 루프와 결이 맞는다 |
| `code-review` | `mattpocock/skills` | 공통 DoD의 리뷰 단계 |
| `diagnosing-bugs` | `mattpocock/skills` | `/fix-error` 를 뒷받침하는 깊은 진단 절차 |

**선정 기준 셋** — ① 우리 스택과 직접 맞을 것 ② 벤더 공식이거나 설치 수로 검증됐을 것 ③ 우리 문서가 이미 정한 것과 충돌하지 않을 것.

### 3.1.1 작업 방식 스킬 4종 (v1.1 추가)

출처는 `wild-mental/{grill-it,goal-setting,review-merge,merge-review}-skill` 이며 **사용자가 지정해 설치**했다. 앞의 8종이 *무엇을 어떻게 만드는가*를 다룬다면, 이 넷은 *어떻게 일할 것인가*를 다룬다.

| 스킬 | 무엇을 하나 | 이 프로젝트에서 |
| --- | --- | --- |
| **`grill-it`** | 착수 전 미해소 결정 토픽을 전부 추출·가시화하고, 의존 순서대로 하나씩 해소하며 **설계문서와 하네스에 즉시 반영**한다. 재개 가능한 Grill Ledger를 남긴다 | **이미 같은 일을 손으로 했다** — SRS 10.3 미결 의존성 16건을 CALC·FXT로 해소하고 태스크 리스트·하네스에 반영한 과정이 정확히 이 절차다. 다음 결정 묶음(🟡 5건 재개 시)에 그대로 쓴다 |
| **`goal-setting`** | `/goal` 프롬프트를 필수 4섹션(목표·범위 / 세부 규칙 / 종료 조건 / 제약)으로 설계. 실현성·시연성·유계성 3원칙 강제 | 태스크 59건을 에이전트에 위임할 때 **종료 조건을 명시**하게 한다. 우리 DoD 8항목이 그대로 종료 조건이 된다 |
| **`review-merge`** | PR을 한 건씩 검토하고 **매 건이 게이트를 통과한 뒤에만** 머지 (REVIEW → MERGE) | **독립 태스크에 쓴다** — 슬랙이 큰 38건은 서로 무관해 개별 게이트 통과가 자연스럽다 |
| **`merge-review`** | 응집·의존 결합된 PR 묶음을 bottom-up으로 먼저 머지하고 **수렴된 화면에서 통합 검토** (MERGE → REVIEW) | **의존 사슬에 쓴다** — `BE-06 → BE-08 → BE-09` 처럼 앞 PR이 뒤 PR 없이는 dead code인 묶음, `FE-03`(한 화면 8건)처럼 통합돼야 동작이 존재하는 경우 |

> **둘은 중복이 아니라 상보다.** PR 묶음의 응집도가 갈림길이다 — 독립이면 `review-merge`, 결합이면 `merge-review`. 우리 태스크 그래프는 두 성격이 섞여 있어(임계 9건은 사슬, 슬랙 큰 38건은 독립) 둘 다 필요하다.

**벤더 판이 세 가지(`.claude` / `.agents` / `.cursor`)로 제공되는데 `.claude` 판을 설치했다.** 슬래시 호출 형식과 `CLAUDE.md` 참조가 우리 환경에 맞는다.

### 3.2 미채택과 이유

| 스킬 | 왜 안 썼나 |
| --- | --- |
| `prisma-mongodb-upgrade` · `prisma-driver-adapter` · `prisma-compute` · `prisma-upgrade-v7` | 우리 스택에 없는 경로 |
| `web-design-guidelines` · `frontend-design` | **`DS-01~05`가 이미 정한다.** 디자인 결정이 두 곳에서 갈라지면 안 된다 |
| `setup-pre-commit` | **C-TEC-007a가 "게이트 1개만" 허용한다.** pre-commit 훅을 더하면 검증 경로가 둘이 되어 제약의 취지가 흐려진다 |
| `find-skills` · `grill-me` · `handoff` · `triage` 등 | 생산성 메타 스킬. 개발 목표와 직접 관계 없다 |
| `agent-browser` · `lark-*` | 무관 |
| `.agents` / `.cursor` 벤더 판 | 같은 스킬의 다른 표기. 세 곳을 함께 두면 갱신이 갈라진다 |
| `improve-codebase-architecture` | 아키텍처는 SDD·ADR이 정본이다. 자동 개선 제안이 ADR-02 경계를 흔들 수 있다 |

> **`setup-pre-commit` 미채택이 판단이 들어간 지점이다.** 금지어 스캔을 커밋 시점으로 앞당기면 편하지만, "배포 전 게이트 1개"라는 제약(C-TEC-007a)은 **검증 경로를 하나로 유지하려는 결정**이었다. 편의를 위해 그것을 흐리지 않는다.

### 3.3 설치 방식

skills.sh의 표준 경로는 `npx skills add <owner/repo>` 다. **여기서는 원본 저장소를 직접 받아 필요한 스킬만 골라 넣었다** — 저장소 단위로 설치하면 쓰지 않을 스킬까지 따라오기 때문이다. 갱신이 필요하면 원본 저장소에서 해당 디렉터리만 다시 가져온다.

---

## 4. 이 구성의 한계

1. **외부 스킬은 우리 문서보다 낮은 우선순위다.** 충돌하면 `docs/` 가 이긴다 — 특히 계산 값·판정 SLO·API 스키마
2. **`vercel-react-best-practices`는 React 일반 레퍼런스다.** App Router 고유 사항은 `frontend-shadcn` 에이전트가 보완한다
3. **외부 스킬은 버전이 고정돼 있다.** 원본이 갱신돼도 자동으로 따라오지 않는다
4. **불변식 6은 코드로 강제되는 것과 문서로만 있는 것이 섞여 있다.** I1은 린트(`IN-04`)가, I2·I3는 배포 게이트 ①이 막지만, I4·I5·I6은 **테스트와 리뷰가 유일한 방어선**이다

---

*참조: `wild-mental/AI-multivender-harness-sample` · [skills.sh](https://www.skills.sh/)*

*작성자: 기획 분석가, 검토자: 개발팀 리드*
