# [태스크 리스트] CardFit

**문서 ID:** TASK-CARDFIT-001

**개정 버전:** 1.0

**날짜:** 2026-08-25

**근거 문서:** SRS-CARDFIT-001 v1.0 (`[SRS 문서] CardFit (한글).md`)

**참조 문서:** SDD-CARDFIT-001 (설계) · STD-CARDFIT-001 (테스트) · GTD-CARDFIT-001 (게이트 데이터)

---

## 0. 이 문서를 읽는 법

### 0.1 근거와 범위

본 태스크 리스트는 **SRS 요구사항 27건 · 기술 제약 8건 · 데이터 모델 15테이블 · API 7행**을 실행 가능한 단위로 분해한 것이다.

- SRS에 **명시되지 않은 기능은 추가하지 않았다.** 모든 태스크는 `관련 SRS 섹션` 열로 원문을 지목한다.
- 향후 개선 대상(SRS 7장 — 정기 재진단 · 대량 처리 최적화 · 신뢰도 배지 · 지속 사용 동기)은 **태스크로 만들지 않았다.**
- 조건부 범위(Could — REQ-FUNC-011·012)는 포함하되 `※Could`로 표기했다.

### 0.2 관점 분리

제약에 따라 두 관점을 분리해 별도의 표로 제시한다.

| Part | 관점 | ID 접두어 | 산출물 성격 |
| --- | --- | :---: | --- |
| **A** | 백엔드 · 프론트엔드 · 인프라 구성 | `CT` `MK` `IN` `DA` `BE` `FE` `TS` `QA` | 실행 코드 · 스키마 · 파이프라인 |
| **B** | UI/UX 디자인 | `DS` | 화면 설계 · 문구 · 디자인 시스템 |

### 0.2.1 접두어 정의

| 접두어 | 뜻 | 방법론 Step |
| :---: | --- | :---: |
| `CT` | Contract — API DTO·에러 코드 계약 | 1 |
| `MK` | Mock — 프론트가 백엔드를 기다리지 않게 하는 가짜 응답 | 1 |
| `DA` | Data — 스키마·마이그레이션 | 1 |
| `IN` | Infra — 기반·게이트·관측 | 4 |
| `BE` | Backend — 로직 (`cqrs:` 라벨로 Query/Command 구분) | 2 |
| `FE` | Frontend — 화면 | 2 |
| `TS` | Test — AC를 테스트 코드로 변환 | 3 |
| `QA` | 시스템 전역 검증 (게이트·보안·부하) | 3·4 |
| `DS` | Design — UI/UX | 병렬 |

### 0.3 표기

| 표기 | 뜻 |
| :---: | --- |
| 🔴 | **착수 차단** — 미결 의존성(SRS 10.3)이 풀려야 시작할 수 있다 |
| ※Could | 조건부 범위. Must·Should 완료 후 여유가 있을 때만 착수 |
| H / M / L | 복잡도 — 높음 / 보통 / 낮음 |

### 0.4 복잡도 기준

| 등급 | 기준 |
| :---: | --- |
| **H** | 도메인 판단이 개입하거나, 실패 시 Guardrail 위반으로 이어지거나, 외부 규제·연동에 묶인 것 |
| **M** | 명세가 확정돼 있고 구현 범위가 분명한 것 |
| **L** | 설정·단순 CRUD·표시 로직 |

---

## 1. Part A — 개발 태스크

### 1.0 계약 정의 (CT · MK)

> **방법론 Step 1.** 백엔드와 프론트엔드의 기준점이 되는 계약을 먼저 고정한다. **이 절이 없으면 FE가 BE 완성을 기다린다.**

| Task ID | Epic (도메인) | Feature (기능명) | 관련 SRS 섹션 | 선행 태스크 | 후행 태스크 (Blocks) | 복잡도 |
| --- | --- | --- | --- | --- | --- | :---: |
| CT-001 | Contract/API | Calculation 도메인 Request/Response DTO 정의 | 6.1.3 · 6.1.1 | None | CT-002, CT-003, CT-004, MK-001, BE-033, BE-034 | M |
| CT-002 | Contract/API | Evidence 도메인 DTO 정의 (근거 6항목 스키마) | 6.1.3 · 4.1 REQ-FUNC-006 | CT-001 | MK-002, BE-021a, BE-035 | M |
| CT-003 | Contract/API | Outcome 도메인 DTO 정의 | 6.1.3 · 4.1 REQ-FUNC-010 | CT-001 | MK-004, BE-036 | L |
| CT-004 | Contract/API | **공통 에러 코드 체계 구현** (CF-4001~CF-2001) | **6.1.2** · 4.3 | CT-001 | MK-003, BE-021b, BE-033 | M |
| MK-001 | Contract/Mock | 계산 결과 Mock — 3시나리오 · **유지/변경 두 결론** | 6.1.3 · 9장 ADR-01 | CT-001 | FE-001, FE-002, FE-003, FE-004, FE-005, FE-006, FE-011, FE-017, FE-020, FE-022, FE-023 | M |
| MK-002 | Contract/Mock | 근거 Mock — 6항목 **충족/미달 두 케이스** | 6.1.3 · 4.3 REQ-EXC-002 | CT-002 | FE-012, FE-014 | M |
| MK-003 | Contract/Mock | 예외 응답 Mock — **6종 전건** (CF 코드별) | 6.1.2 · 4.3 | CT-004 | FE-015, FE-018, FE-019 | M |
| MK-004 | Contract/Mock | 완주 계측 Mock | 6.1.3 · 4.1 REQ-FUNC-010 | CT-003 | FE-021 | L |

**`MK-001`은 두 결론을 모두 담아야 한다.** "변경"만 제공하면 `FE-009`(유지 결론 표시)를 개발할 수 없고, ADR-01이 만든 이 제품의 핵심 화면이 마지막까지 미검증으로 남는다.

**`MK-003`은 6종 전건이 필요하다.** 예외 화면(`FE-018`~`FE-020`)은 *"결과를 내지 않는 것이 정답"* 인 경로라, 실제 응답을 만들어 보지 않으면 화면을 설계할 수 없다.

### 1.1 인프라 구성 (IN)

| Task ID | Epic (도메인) | Feature (기능명) | 관련 SRS 섹션 | 선행 태스크 | 후행 태스크 (Blocks) | 복잡도 |
| --- | --- | --- | --- | --- | --- | :---: |
| IN-001 | Infra/Base | Next.js App Router 프로젝트 초기화 | 1.5 C-TEC-001 | None | IN-002, IN-003, IN-004, IN-008, IN-009 | L |
| IN-002 | Infra/Base | Tailwind CSS + shadcn/ui 설정 | 1.5 C-TEC-004 | IN-001 | — | L |
| IN-003 | Infra/Base | Prisma + 로컬 Supabase 개발환경 구성 | 1.5 C-TEC-003 | IN-001 | DA-001 | M |
| IN-004 | Infra/Deploy | Vercel 배포 연결 (Git Push 자동화) | 1.5 C-TEC-007 | IN-001 | IN-005, IN-006, IN-010, IN-011, IN-012, IN-013, IN-014, IN-015, IN-016 | L |
| IN-005 | Infra/Gate | 배포 게이트 ① 경계값 회귀 CI | 1.5 C-TEC-007a | IN-004, BE-020 | QA-004 | M |
| IN-006 | Infra/Gate | 배포 게이트 ② 금지어 정적 스캔 CI | 1.5 C-TEC-007a | IN-004, BE-025 | IN-007, QA-005 | M |
| IN-007 | Infra/Gate | AI 모델 식별자 변경 시 게이트 재실행 트리거 | 1.5.2 갈래② | IN-006, IN-009 | — | M |
| IN-008 | Infra/Arch | **의존성 경계 린트 — ADR-02 강제** | 1.5.1 신규위험① | IN-001 | — | M |
| IN-009 | Infra/AI | Vercel AI SDK + 환경변수 기반 모델 교체 | 1.5 C-TEC-005·006 | IN-001 | IN-007, BE-023, BE-024 | L |
| IN-010 | Infra/Observability | APM 연동 — p50·p95·p99 관측 | 4.2 REQ-NF-001 | IN-004 | BE-037, QA-007 | M |
| IN-011 | Infra/Observability | 실시간 운영 알림 채널 연동 | 11.2 Guardrail | IN-004 | BE-031 | M |
| IN-012 | Infra/Notify | 사용자 발송 채널 연동 | 4.1 REQ-FUNC-010 | IN-004 | BE-027a | M |
| IN-013 | Infra/Observability | 이벤트 분석·집계 도구 연동 | 4.2 REQ-NF-009 | IN-004 | BE-029 | M |
| IN-014 | Infra/Batch | Vercel Cron 배치 스케줄 구성 | 1.5.2 갈래③ | IN-004 | BE-004, BE-013, BE-027a, BE-032a | M |
| IN-015 | Infra/Perf | 서버리스 실행 시간 상한 실측 | 1.5.2 갈래③ · D15 | IN-004, BE-016 | — | M |
| 🔴 IN-016 | Infra/Integration | 마이데이터 연동 경로 구성 (고정IP·인증서) | 1.5.2 갈래① · **D11** | IN-004 | BE-005 | H |

> **IN-008을 1스프린트에 넣는다.** 코드가 쌓인 뒤에 경계를 세우면 이미 넘어간 의존성을 되돌려야 한다. 단일 코드베이스에서는 `import` 한 줄로 ADR-02가 깨진다.

### 1.2 데이터 계층 (DA)

| Task ID | Epic (도메인) | Feature (기능명) | 관련 SRS 섹션 | 선행 태스크 | 후행 태스크 (Blocks) | 복잡도 |
| --- | --- | --- | --- | --- | --- | :---: |
| DA-001 | Data/Schema | `users` — 동의 상태·범위·일시 — 스키마 + 마이그레이션 스크립트 | 6.4.2 | IN-003 | DA-002, DA-003, DA-004, DA-006, DA-011, BE-001, BE-003 | M |
| DA-002 | Data/Schema | `card_products` · `held_cards` — 스키마 + 마이그레이션 스크립트 | 6.4.2 | DA-001 | DA-005, BE-005 | M |
| DA-003 | Data/Schema | `past_spends` + 조회 인덱스 — 스키마 + 마이그레이션 스크립트 | 6.4.2 · 6.6 | DA-001 | BE-005, BE-009 | M |
| DA-004 | Data/Schema | `future_spend_plans` · `user_constraints` — 스키마 + 마이그레이션 스크립트 | 6.4.2 | DA-001 | DA-007, BE-008, BE-010, BE-011 | M |
| DA-005 | Data/Schema | `benefit_rules` + 약관 원문·요약 필드 — 스키마 + 마이그레이션 스크립트 | 6.4.2 · 9장 ADR-02 | DA-002 | DA-007, DA-012, BE-012, BE-013, BE-021a, BE-023, BE-032a | M |
| DA-006 | Data/Schema | `calculations` · `calculation_scenarios` — 스키마 + 마이그레이션 스크립트 | 6.4.2 | DA-001 | DA-007, DA-008, DA-010, DA-012, BE-006 | M |
| DA-007 | Data/Schema | `calculation_input_plans` · `calculation_applied_rules` — 스키마 + 마이그레이션 스크립트 | 6.4.1 · 6.4.3 | DA-004, DA-005, DA-006 | — | M |
| DA-008 | Data/Schema | `plan_candidates` · `allocations` — 스키마 + 마이그레이션 스크립트 | 6.4.2 | DA-006 | DA-009, DA-012, BE-018, BE-030 | M |
| DA-009 | Data/Schema | `outcome_logs` — 스키마 + 마이그레이션 스크립트 | 6.4.2 · 6.5 | DA-008 | BE-027a | L |
| DA-010 | Data/Audit | `audit_logs` + append-only 권한 설정 — 스키마 + 마이그레이션 스크립트 | 6.4.2 · 4.2 REQ-NF-006 | DA-006 | BE-028 | M |
| DA-011 | Data/Security | **Supabase RLS 정책 — 행 단위 소유권** | 1.5.1 강화 · 4.2 REQ-NF-004 | DA-001~010 | BE-002, QA-006 | H |
| DA-012 | Data/Integrity | 금액 `BIGINT` 원 단위 정수 정책 적용 | 6.4.3 | DA-005, DA-006, DA-008 | BE-012 | L |

### 1.3 백엔드 (BE)

| Task ID | Epic (도메인) | Feature (기능명) | 관련 SRS 섹션 | 선행 태스크 | 후행 태스크 (Blocks) | 복잡도 |
| --- | --- | --- | --- | --- | --- | :---: |
| BE-001 | Auth | 인증·세션 처리 ※방식은 SRS 미명시 | 4.2 REQ-NF-004 | DA-001 | BE-002 | M |
| BE-002 | Auth | `AccessOwnershipVerifier` — 응답 주체 전건 대조 | 4.2.1 · 4.2 REQ-NF-004 | BE-001, DA-011 | BE-031, QA-006 | H |
| BE-003 | MyData | `ConsentGuard` — 동의 상태 판정 | 4.3 REQ-EXC-004 · 6.5 | DA-001 | BE-004 | M |
| BE-004 | MyData | 동의 철회 후 24시간 내 파기 배치 | 4.2 REQ-NF-004 | BE-003, IN-014 | — | M |
| 🔴 BE-005 | MyData | `MyDataConnector` — 과거소비·보유카드 수집 | 4.1 REQ-FUNC-002 | IN-016, DA-002, DA-003 | BE-006, BE-007, BE-009 | H |
| BE-006 | MyData | `CallBudgetCounter` — DB 기반 호출 예산 통제 | 4.2 REQ-NF-005 | BE-005, DA-006 | BE-033 | M |
| BE-007 | MyData | `DegradedModeHandler` — 장애 시 스냅샷 폴백 | 4.3.1 REQ-EXC-003 | BE-005 | — | M |
| BE-008 | Input | `FutureSpendPlanService` — 자유 카테고리·증감 양방향 | 4.1 REQ-FUNC-001·008 | DA-004 | BE-039 | M |
| BE-009 | Input | `InitialValueSuggester` — 과거 패턴 초기값 제안 | 4.1 REQ-FUNC-007 | BE-005, DA-003 | — | H |
| BE-010 | Input | 제약조건 저장 (카드수·연회비상한·발급허용) | 4.1 REQ-FUNC-002 | DA-004 | — | L |
| 🔴 BE-011 | Calc | `ScenarioBuilder` — 시나리오 3개 생성 | 4.1 REQ-FUNC-003 · **D5** | DA-004 | BE-016 | M |
| 🔴 BE-012 | Calc | **`RuleEngine` 계산 코어** (실적구간·한도·연회비·제외) | 4.1.0 RE-1~4 · **D16** | DA-005, DA-012 | BE-014, BE-015, BE-016, BE-020, BE-021a | H |
| BE-013 | Calc | `RuleFreshnessChecker` — 30일 초과 카드 제외 | 4.2 REQ-NF-007 | DA-005, IN-014 | — | M |
| 🔴 BE-014 | Calc | `NetBenefitEvaluator` — **전환비용 3항목 산정** | 4.1.0 **RE-5** · 4.1 REQ-FUNC-004 | BE-012 | BE-017 | H |
| 🔴 BE-015 | Calc | `CombinationGenerator` — 조합 후보 생성 | 4.1.0 RE-6·RE-7 · **D16** | BE-012 | BE-016, BE-019, BE-026, BE-038 | H |
| BE-016 | Calc | `CalculationOrchestrator` — 3시나리오 조정 + 부분 판정 | 4.1.1 · 4.3 REQ-EXC-005 | BE-011, BE-012, BE-015 | IN-015, BE-033, BE-034, QA-007 | H |
| 🔴 BE-017 | Calc | **`GatingPolicy` — 게이팅 판정** | 4.1.1 ② · 4.1 REQ-FUNC-004 · **D2** | BE-014 | — | M |
| BE-018 | Calc | `PlanExpiryPolicy` — rule_version·+30일 만료 | 4.3 REQ-EXC-006 · 9장 ADR-06 | DA-008 | — | M |
| 🔴 BE-019 | Calc | `AllocationService` — 배분 + 합계 오차 ≤ 1원 검증 | 4.1 REQ-FUNC-005 · 4.1.0 **RE-8** | BE-015 | — | M |
| 🔴 BE-020 | Calc/QA | `DeterminismVerifier` + 경계값 회귀 스위트 | 4.2 REQ-NF-002 · **D16** | BE-012 | IN-005, QA-004 | H |
| BE-021a | Evidence | `EvidenceAssembler` — 근거 6항목 조립 `cqrs:query` | 4.1 REQ-FUNC-006 | BE-012, DA-005, CT-002 | BE-021b, BE-022, BE-024 | M |
| BE-021b | Evidence | **6항목 게이트 — 미달 시 `CF-4221` 거부** `policy` | 4.3 REQ-EXC-002 · GR3 | BE-021a, CT-004 | BE-035 | M |
| BE-022 | Evidence | 미반영 항목 산출·표기 | 4.1 REQ-FUNC-006 | BE-021a | — | M |
| BE-023 | AI | `summarizeTerms` — 약관 요약 + rule_version 캐시 | 9장 ADR-02 · 1.5.3 **DEC-3a** | IN-009, DA-005 | — | M |
| 🔴 BE-024 | AI | `describeRationale` — 추천 근거 자연어 설명 | 9장 ADR-02 · 1.5.3 **DEC-3b** | IN-009, BE-021a | — | M |
| BE-025 | Compliance | `ProhibitedTermScanner` — 런타임 문구 스캔 | 4.1 REQ-FUNC-009 | (D8 해소) | IN-006, QA-005 | M |
| BE-026 | Compliance | `ScopeBoundaryNotice` — 경계 안내 생성 | 4.1 REQ-FUNC-009 | BE-015 | — | L |
| BE-027a | Tracking | 선택 기록 · +30일 1회 발송 `cqrs:command` | 4.1 REQ-FUNC-010 · 6.5 | DA-009, IN-012, IN-014 | BE-027b, BE-036 | M |
| BE-027b | Tracking | 완주율 집계 — 무응답 = 미완주 `cqrs:query` | 4.1 REQ-FUNC-010 · 11.2 | BE-027a | — | M |
| BE-028 | Audit | `AuditRecorder` — 전건 적재 | 4.2 REQ-NF-006 | DA-010 | — | M |
| BE-029 | Metric | `MetricEventEmitter` — 7종 이벤트 적재 | 4.2 REQ-NF-009 | IN-013 | BE-030, FE-024 | M |
| BE-030 | Metric | `NorthStarCalculator` — **분모 제외 로직** | 11.1 · 9장 ADR-05 | BE-029, DA-008 | — | M |
| BE-031 | Guardrail | `GuardrailMonitor` — 5건 감시·중단 판정 | 11.2 | BE-002·017·021b·025, IN-011 | — | H |
| 🔴 BE-032a | RuleData | 약관 수집 · `rule_version` 발행 `cqrs:command` | 4.2 REQ-NF-007 · **D4** | DA-005, IN-014 | BE-032b | H |
| BE-032b | RuleData | 최신성 점검 · 30일 초과 제외 판정 `cqrs:query` | 4.2 REQ-NF-007 | BE-032a | — | M |
| BE-033 | API | `POST /api/v1/calculate` | 6.1.3 | BE-016, BE-006, CT-001, CT-004 | — | M |
| BE-034 | API | `GET /api/v1/calculations/{id}` | 6.1.3 | BE-016, CT-001 | — | L |
| BE-035 | API | `GET /api/v1/calculations/{id}/evidence` | 6.1.3 | BE-021b, CT-002 | — | M |
| BE-036 | API | `POST /api/v1/outcomes/{id}/completion` | 6.1.3 | BE-027a, CT-003 | — | L |
| BE-037 | Observability | `LatencyInterceptor` — 엔드포인트 레이턴시 계측 | 4.2 REQ-NF-001 | IN-010 | — | L |
| BE-038 | Calc | `StagedTransitionPresenter` — 단계적 전환 제안 ※Could | 4.1 REQ-FUNC-011 | BE-015 | — | L |
| BE-039 | Input | 소득·지출 범위 입력 처리 ※Could | 4.1 REQ-FUNC-012 | BE-008 | — | L |

### 1.4 프론트엔드 (FE)

| Task ID | Epic (도메인) | Feature (기능명) | 관련 SRS 섹션 | 선행 태스크 | 후행 태스크 (Blocks) | 복잡도 |
| --- | --- | --- | --- | --- | --- | :---: |
| FE-001 | Onboarding | 마이데이터 동의 화면 | 8.3 · 4.1 REQ-FUNC-002 | DS-002, MK-001 | — | M |
| FE-002 | Onboarding | 초기값 제안 확인·수정 화면 | 4.1 REQ-FUNC-007 | DS-003, MK-001 | — | M |
| FE-003 | Input | 미래지출 입력 폼 (자유 카테고리·증감 양방향) | 4.1 REQ-FUNC-001·008 | DS-003, MK-001 | — | M |
| FE-004 | Input | 제약조건 입력 화면 | 4.1 REQ-FUNC-002 | DS-003, MK-001 | — | L |
| FE-005 | Result | 계산 진행 상태 화면 | 4.2 REQ-NF-001 | DS-004, MK-001 | — | L |
| FE-006 | Result | 결과 화면 — **"예상대로" 기본 탭** | 6.3 규칙6 · 4.1 REQ-FUNC-004 | DS-004, MK-001 | FE-007, FE-009, FE-010 | M |
| FE-007 | Result | 시나리오 탭 전환 — **재계산 없음** | 9장 ADR-03 · 4.1 REQ-FUNC-003 | FE-006 | FE-008 | M |
| FE-008 | Result | 탭별 지출 가정 캡션 | 6.3 규칙7 | FE-007 | — | L |
| FE-009 | Result | **"현재 조합 유지" 결론 표시** | 9장 ADR-01 · 4.1 REQ-FUNC-004 | DS-005, FE-006 | — | M |
| FE-010 | Result | 조합 변경안 + **차액 원 단위** 표시 | 5.1 AC-01 | FE-006 | — | M |
| FE-011 | Result | 카드별 역할·배분안 화면 | 4.1 REQ-FUNC-005 | DS-005, MK-001 | — | M |
| FE-012 | Evidence | 근거 화면 — 6항목 펼침 | 4.1 REQ-FUNC-006 | DS-006, MK-002 | FE-013, FE-014 | M |
| FE-013 | Evidence | 미반영 항목 표기 | 4.1 REQ-FUNC-006 | FE-012 | — | L |
| FE-014 | Evidence | AI 약관 요약·근거 설명 표시 | 9장 ADR-02 | FE-012, MK-002 | — | M |
| FE-015 | Compliance | 스코프 경계 안내 노출 | 4.1 REQ-FUNC-009 | DS-007, MK-003 | FE-016 | L |
| FE-016 | Compliance | 카드사 공식 신청 페이지 이동 링크 | 1.2 범위 | FE-015 | — | L |
| FE-017 | Tracking | 조합안 선택·저장 | 11.1 북극성 | MK-001 | — | M |
| FE-018 | Exception | 만료 조합안 표기·재계산 유도 | 4.3 REQ-EXC-006 | DS-007, MK-003 | — | M |
| FE-019 | Exception | 마이데이터 장애 경고 + **기준일 표시** | 4.3.1 REQ-EXC-003 | DS-007, MK-003 | — | M |
| FE-020 | Exception | 예외 화면 — 400 / 응답거부 / 부분처리 | 4.3 REQ-EXC-001·002·005 | DS-007, MK-001 | — | M |
| FE-021 | Tracking | 완주 확인 응답 화면 | 4.1 REQ-FUNC-010 | DS-008, MK-004 | — | L |
| FE-022 | Result | 단계적 전환 제안 표시 ※Could | 4.1 REQ-FUNC-011 | MK-001 | — | L |
| FE-023 | Input | 소득·지출 범위 입력 UI ※Could | 4.1 REQ-FUNC-012 | MK-001 | — | L |
| FE-024 | Metric | 이벤트 계측 삽입 (7종) | 4.2 REQ-NF-009 | BE-029 | — | M |

### 1.5 테스트 코드 작성 (TS)

> **방법론 Step 3.** STD의 인수 조건(GWT)을 **테스트 코드 작성 태스크**로 변환한다. 요구사항 27건 · TC 27건과 **1:1**이며, 각 TS는 대응 Feature 태스크의 DoD 체크리스트에 삽입된다.

| Task ID | Epic (도메인) | Feature (기능명) | 관련 SRS 섹션 | 선행 태스크 | 후행 태스크 (Blocks) | 복잡도 |
| --- | --- | --- | --- | --- | --- | :---: |
| TS-001 | QA/Test | [Test] TC-FUNC-001 GWT 시나리오 테스트 코드 작성 | STD TC-FUNC-001 | 대응 Feature 태스크 | — | M |
| TS-002 | QA/Test | [Test] TC-FUNC-002 GWT 시나리오 테스트 코드 작성 | STD TC-FUNC-002 | 대응 Feature 태스크 | — | M |
| TS-003 | QA/Test | [Test] TC-FUNC-003 GWT 시나리오 테스트 코드 작성 | STD TC-FUNC-003 | 대응 Feature 태스크 | — | M |
| TS-004 | QA/Test | [Test] TC-FUNC-004 GWT 시나리오 테스트 코드 작성 | STD TC-FUNC-004 | 대응 Feature 태스크 | — | M |
| TS-005 | QA/Test | [Test] TC-FUNC-005 GWT 시나리오 테스트 코드 작성 | STD TC-FUNC-005 | 대응 Feature 태스크 | — | M |
| TS-006 | QA/Test | [Test] TC-FUNC-006 GWT 시나리오 테스트 코드 작성 | STD TC-FUNC-006 | 대응 Feature 태스크 | — | M |
| TS-007 | QA/Test | [Test] TC-FUNC-007 GWT 시나리오 테스트 코드 작성 | STD TC-FUNC-007 | 대응 Feature 태스크 | — | M |
| TS-008 | QA/Test | [Test] TC-FUNC-008 GWT 시나리오 테스트 코드 작성 | STD TC-FUNC-008 | 대응 Feature 태스크 | — | M |
| TS-009 | QA/Test | [Test] TC-FUNC-009 GWT 시나리오 테스트 코드 작성 | STD TC-FUNC-009 | 대응 Feature 태스크 | — | M |
| TS-010 | QA/Test | [Test] TC-FUNC-010 GWT 시나리오 테스트 코드 작성 | STD TC-FUNC-010 | 대응 Feature 태스크 | — | M |
| TS-011 | QA/Test | [Test] TC-FUNC-011 GWT 시나리오 테스트 코드 작성 | STD TC-FUNC-011 | 대응 Feature 태스크 | — | M |
| TS-012 | QA/Test | [Test] TC-FUNC-012 GWT 시나리오 테스트 코드 작성 | STD TC-FUNC-012 | 대응 Feature 태스크 | — | M |
| TS-013 | QA/Test | [Test] TC-NF-001 GWT 시나리오 테스트 코드 작성 | STD TC-NF-001 | 대응 Feature 태스크 | — | M |
| TS-014 | QA/Test | [Test] TC-NF-002 GWT 시나리오 테스트 코드 작성 | STD TC-NF-002 | 대응 Feature 태스크 | — | M |
| TS-015 | QA/Test | [Test] TC-NF-003 GWT 시나리오 테스트 코드 작성 | STD TC-NF-003 | 대응 Feature 태스크 | — | M |
| TS-016 | QA/Test | [Test] TC-NF-004 GWT 시나리오 테스트 코드 작성 | STD TC-NF-004 | 대응 Feature 태스크 | — | M |
| TS-017 | QA/Test | [Test] TC-NF-005 GWT 시나리오 테스트 코드 작성 | STD TC-NF-005 | 대응 Feature 태스크 | — | M |
| TS-018 | QA/Test | [Test] TC-NF-006 GWT 시나리오 테스트 코드 작성 | STD TC-NF-006 | 대응 Feature 태스크 | — | M |
| TS-019 | QA/Test | [Test] TC-NF-007 GWT 시나리오 테스트 코드 작성 | STD TC-NF-007 | 대응 Feature 태스크 | — | M |
| TS-020 | QA/Test | [Test] TC-NF-008 GWT 시나리오 테스트 코드 작성 | STD TC-NF-008 | 대응 Feature 태스크 | — | M |
| TS-021 | QA/Test | [Test] TC-NF-009 GWT 시나리오 테스트 코드 작성 | STD TC-NF-009 | 대응 Feature 태스크 | — | M |
| TS-022 | QA/Test | [Test] TC-EXC-001 GWT 시나리오 테스트 코드 작성 | STD TC-EXC-001 | 대응 Feature 태스크 | — | M |
| TS-023 | QA/Test | [Test] TC-EXC-002 GWT 시나리오 테스트 코드 작성 | STD TC-EXC-002 | 대응 Feature 태스크 | — | M |
| TS-024 | QA/Test | [Test] TC-EXC-003 GWT 시나리오 테스트 코드 작성 | STD TC-EXC-003 | 대응 Feature 태스크 | — | M |
| TS-025 | QA/Test | [Test] TC-EXC-004 GWT 시나리오 테스트 코드 작성 | STD TC-EXC-004 | 대응 Feature 태스크 | — | M |
| TS-026 | QA/Test | [Test] TC-EXC-005 GWT 시나리오 테스트 코드 작성 | STD TC-EXC-005 | 대응 Feature 태스크 | — | M |
| TS-027 | QA/Test | [Test] TC-EXC-006 GWT 시나리오 테스트 코드 작성 | STD TC-EXC-006 | 대응 Feature 태스크 | — | M |

### 1.6 시스템 전역 검증 (QA)

특정 기능이 아니라 시스템 전체를 대상으로 하므로 Feature 1:1 대응이 성립하지 않는다.

| Task ID | Epic (도메인) | Feature (기능명) | 관련 SRS 섹션 | 선행 태스크 | 후행 태스크 (Blocks) | 복잡도 |
| --- | --- | --- | --- | --- | --- | :---: |
| QA-004 | QA/Gate | 경계값 회귀 스위트 게이트 연결 (260건) | 1.5 C-TEC-007a · GTD 1장 | BE-020, IN-005 | — | M |
| QA-005 | QA/Gate | 금지어 스캐너 샘플 회귀 (31건) | 1.5 C-TEC-007a · GTD 2장 | BE-025, IN-006 | — | L |
| QA-006 | QA/Security | **RLS ↔ 애플리케이션 이중화 독립 검증** | 4.2.1 · 4.2 REQ-NF-004 | DA-011, BE-002 | — | H |
| QA-007 | QA/Perf | 부하 테스트 — 카드 3·5·10장 | 4.2 REQ-NF-001 | IN-010, BE-016 | — | M |

---

## 2. Part B — UI/UX 디자인 태스크 (DS)

| Task ID | Epic (도메인) | Feature (기능명) | 관련 SRS 섹션 | 선행 태스크 | 후행 태스크 (Blocks) | 복잡도 |
| --- | --- | --- | --- | --- | --- | :---: |
| DS-001 | Design System | shadcn/ui 기반 디자인 토큰·컴포넌트 정의 | 1.5 C-TEC-004 | None | DS-002, DS-003, DS-004, DS-007, DS-008, DS-009 | M |
| DS-002 | Onboarding | 마이데이터 동의 화면 설계 (동의 범위 최소 노출) | 8.3 · 4.2 REQ-NF-004 | DS-001 | FE-001 | M |
| DS-003 | Input Flow | 입력 플로우 설계 — **직접 입력 강제 0개** · 자유 카테고리 · 증감 양방향 | 4.1 REQ-FUNC-001·007·008 · 8.1 | DS-001 | FE-002, FE-003, FE-004 | H |
| DS-004 | Result | 결과 화면 설계 — **기본 탭 1개 + 보조 탭 2개** 구조 | 6.3 규칙6 · 9장 ADR-03 | DS-001 | FE-005, FE-006, DS-005, DS-006 | H |
| DS-005 | Result | **"유지" 결론 표현 설계** — 실패로 보이지 않게 | 9장 ADR-01 · 8.1 | DS-004 | FE-009, FE-011 | H |
| DS-006 | Evidence | 근거 화면 설계 — 6항목 + 미반영 항목 | 4.1 REQ-FUNC-006 · 8.1 | DS-004 | FE-012 | H |
| DS-007 | Compliance | 경계 안내·예외 화면 문구 설계 | 4.1 REQ-FUNC-009 · 4.3 | DS-001 | FE-015, FE-018, FE-019, FE-020 | M |
| DS-008 | Tracking | 완주 확인 발송·응답 화면 설계 (**독려 없이**) | 4.1 REQ-FUNC-010 · 9장 ADR-04 | DS-001 | FE-021 | L |
| DS-009 | Ops | 운영 대시보드 설계 — 지표 4층 + Guardrail 5건 | 11.2 | DS-001 | — | M |

> **DS-005가 이 제품에서 가장 어려운 디자인 문제다.** *"그대로 두세요"* 를 실패나 오류로 보이지 않게 표현해야 한다. 사용자는 무언가 바뀌기를 기대하고 들어왔고, 화면은 아무것도 바꾸지 말라고 답한다. 이 표현이 어색하면 ADR-01의 정직함이 사용자에게는 무성의로 읽힌다.

---

## 3. 착수 차단 태스크

| 차단 의존성 | 막힌 태스크 | 성격 | 해소 주체 |
| :---: | --- | --- | --- |
| **D16** 규칙 엔진 계산 명세 (RE-1~8) | BE-012 · BE-014 · BE-015 · BE-019 · BE-020 | 계산 로직 자체 | **기획 결정** |
| **D2** Net Benefit 임계값 | BE-017 | 판정 기준값 | 기획 결정 (**RE-5 선행**) |
| **D5** 시나리오 증감 폭 | BE-011 | 계산 기준값 | 기획 결정 |
| **D11** 마이데이터 연동 가능성 | IN-016 · BE-005 | 규제·기술 확인 | 컴플라이언스 + 인프라 |
| **D4** 지원 카드사 범위 | BE-032a | 운영 역량 산정 | 데이터 운영 |
| **DEC-3b** 금융정보 외부 AI 전송 | BE-024 | 국외 이전 검토 | 컴플라이언스 |

**D16이 5개 태스크를 동시에 막는다.** 계산 코어(BE-012)가 막히면 그 위의 전환비용·조합생성·배분·회귀스위트가 전부 막힌다. **D16 → D2 순서로 풀어야 하며**, 순서를 뒤집으면 전환비용 산정 기준 없이 임계값을 정하게 되어 임계값이 무의미해진다(SRS 4.1.0 RE-5).

---

## 4. 착수 순서 제안

차단이 없는 것부터 쌓는다.

| 스프린트 | 태스크 | 근거 |
| :---: | --- | --- |
| **1** | **CT-001~004** · IN-001~004 · **IN-008** · DS-001 · DA-001~004 · DA-012 | 계약 우선. IN-008을 여기 넣는 이유는 0.1절 참고 |
| **2** | **MK-001~004** · DA-005~010 · BE-001·003·008·010 · DS-002~003 · IN-009 | Mock이 나오면 FE가 BE를 기다리지 않는다 |
| **3** | **FE 전반** · DA-011 · BE-002 · QA-006 · IN-010~014 · DS-004~007 | Mock 기반 FE 착수 + 보안 이중화 |
| **4+** | 🔴 해소 후 BE-011~020 · TS-001~027 · QA-004·005·007 | 계산 도메인은 D16·D2 확정 이후 |

**1~3스프린트는 미결 의존성과 무관하게 진행할 수 있다.** 계산 도메인(BE-011~020)만 D16·D2에 묶여 있으므로, 그 사이에 계약·기반·입력·보안·관측·화면을 완성해 두면 임계값 확정 즉시 계산 도메인에 집중할 수 있다.

**3스프린트에 FE가 들어온 것이 Mock 도입의 효과다.** 이전 배열에서 FE는 4스프린트 이후였다.

---

## 5. 통계

| 구분 | 건수 |
| --- | :---: |
| Part A — 개발 | **133** (CT 4 · MK 4 · IN 16 · DA 12 · BE 42 · FE 24 · TS 27 · QA 4) |
| Part B — 디자인 | **9** |
| **합계** | **142** |
| 착수 차단 🔴 | 9 |
| 조건부 범위 ※Could | 4 |
| 위상 계층 | **10** (Mock 도입 전 13) |
| 의존 엣지 | 164 |

**후행 태스크(Blocks) 열은 `tools/build_task_graph.py --write`로 생성한다.** 수동으로 고치지 않는다 — 선행 열이 바뀌면 다시 생성해야 어긋나지 않는다.

---

## 6. 이 리스트의 한계

1. **`BE-001`(인증·세션)은 방식이 미명시다.** SRS 4.2 REQ-NF-004가 *"모든 API에 인증 요구"* 만 규정하고 인증 수단·회원가입 플로우를 정하지 않았다. 상상해 넣지 않았으므로, 착수 전에 방식을 결정해야 한다.
2. **`IN-010`~`IN-013`은 도구가 미선정이다.** SRS 1.5.2 갈래④가 *"스택에 수단이 없다"* 고 식별한 항목(APM · 알림 · 발송 · 분석)이며, 도구 선정이 선행된다.
3. **복잡도는 상대 등급이다.** 인시(man-hour) 추정이 아니라 태스크 간 상대 난이도이며, 실제 일정 산정에는 팀 역량을 반영해야 한다.
4. **선행 태스크는 기술 의존성만 표기했다.** 조직·인력 배분에서 오는 순서 제약은 반영하지 않았다.

---

*근거 문서: `[SRS 문서] CardFit (한글).md` (SRS-CARDFIT-001 v1.0)*

*작성자: 기획 분석가, 검토자: 개발팀 리드, 승인자: 제품 책임자 (PM)*
