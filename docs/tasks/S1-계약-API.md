# [태스크 명세 · 배치 1] 계약 — API (CT-001 ~ CT-004)

**문서 ID:** ISSUE-CARDFIT-S1-API

**개정 버전:** 1.0

**날짜:** 2026-08-25

**근거 문서:** TASK-CARDFIT-001 v1.1 (`../[태스크 리스트] CardFit.md`) · SRS-CARDFIT-001 §6.1

**템플릿:** `.github/ISSUE_TEMPLATE/feature-task.md` (TPL-CARDFIT-001)

**방법론 단계:** Step 1 — 계약 및 규약 · 추출 대상 2 (API 및 통신 계약)

---

## 0. 이 배치를 먼저 쓰는 이유

**CT-001 하나가 6개 태스크를 막고 있다**(CT-002·003·004 · MK-001 · BE-033 · BE-034). 계약이 없으면 BE는 응답 형태를 임의로 정하고, FE는 그것을 기다리며, Mock은 만들 대상이 없다.

배치 1을 끝내면 **`MK-001`~`MK-004`가 즉시 착수 가능**해지고, 그 시점에서 FE 24건의 BE 직렬 의존이 풀린다.

| 태스크 | 복잡도 | Blocks | 라벨 |
| :---: | :---: | --- | --- |
| CT-001 | M | CT-002·003·004 · MK-001 · BE-033·034 | `epic:api` `layer:ct` `priority:p1` `contract:api` |
| CT-002 | M | MK-002 · BE-021a · BE-035 | `epic:api` `layer:ct` `priority:p1` `contract:api` |
| CT-003 | L | MK-004 · BE-036 | `epic:api` `layer:ct` `priority:p2` `contract:api` |
| CT-004 | M | MK-003 · BE-021b · BE-033 | `epic:api` `layer:ct` `priority:p0` `contract:api` |

> **CT-004가 `priority:p0`인 이유** — 에러 코드 체계는 `CF-4221`(근거 미달, GR3)과 `CF-4030`(오조회, GR5)을 포함한다. Guardrail 2건의 판정 결과를 실어 나르는 통로라 P0다.

**공통 기술 전제** — C-TEC-001·002에 따라 Next.js App Router 단일 코드베이스이며, DTO는 **TypeScript 타입 + 런타임 스키마 검증**으로 구현한다. 검증 라이브러리는 미지정이므로 팀 표준을 따른다(본 문서는 Zod를 예시로 표기하되 강제하지 않는다).

---

## CT-001

```markdown
---
name: Feature Task
about: SRS 기반의 구체적인 개발 태스크 명세
title: "[Feature] CT-001: Calculation 도메인 Request/Response DTO 정의"
labels: 'feature, contract:api, epic:api, layer:ct, priority:p1'
assignees: ''
---

## 🎯 Summary
- 기능명: [CT-001] Calculation 도메인 Request/Response DTO 정의
- 목적: 계산 요청·응답의 타입과 런타임 검증 규칙을 한 곳에 고정해, 백엔드·프론트엔드·Mock이 동일한 계약을 참조하게 한다.

## 🔗 References (Spec & Context)
> 💡 AI Agent & Dev Note: 작업 시작 전 아래 문서를 반드시 먼저 Read/Evaluate 할 것.
- SRS 문서: [`/docs/[SRS 문서] CardFit (한글).md` §6.1.3 엔드포인트별 요청·응답](#613-엔드포인트별-요청응답)
- 공통 응답 봉투: [`§6.1.1 공통 응답 봉투`](#611-공통-응답-봉투)
- 데이터 모델 (enum): [`§6.2 데이터 모델 정의`](#62-데이터-모델-정의) — `ScenarioType` · `CalculationStatus` · `GatingResult` · `TransitionCostItem`
- 시퀀스 다이어그램: [`/docs/[설계 문서] CardFit (한글).md` §5.1 SD-01 정상 계산](#51-sd-01-정상-계산--3개-시나리오-사전-계산)
- 관련 요구사항: `REQ-FUNC-003`(시나리오 3개) · `REQ-FUNC-004`(게이팅) · `REQ-EXC-001`(미래 입력 0건)

## ✅ Task Breakdown (실행 계획)
- [ ] 계약 모듈 디렉터리 생성 — BE·FE·Mock이 함께 import 하는 단일 위치 (예: `src/contracts/calculation/`)
- [ ] 공통 응답 봉투 타입 `ApiResponse<T>` 정의 — `data?` / `warning?` / `error?` 3키, 실패 시 `data` 키 자체를 생략
- [ ] SRS §6.2의 enum 4종을 계약 타입으로 옮김 — `ScenarioType`(LESS·AS_EXPECTED·MORE) · `CalculationStatus`(REQUESTED·SUCCESS·FAILED·PARTIAL) · `GatingResult`(KEEP_CURRENT·RECOMMEND_CHANGE) · `TransitionCostItem`
- [ ] `CalculateRequest` 스키마 작성 — `futureSpendPlanIds: int64[]` **최소 1건** · `constraintId?: int64`
- [ ] `CalculationResponse` 스키마 작성 — `calculationId` · `status` · `baseDate` · `scenarios[]` · `defaultScenario`
- [ ] `scenarios` 배열 길이를 **정확히 3**으로 제약하고, `scenarioType` 3종이 중복 없이 모두 존재하는지 검증 규칙 추가
- [ ] `defaultScenario`를 `AS_EXPECTED` 리터럴로 고정 (SRS §6.3 규칙6)
- [ ] `ScenarioResult` 스키마 — `scenarioType` · `assumptionCaption`(필수) · `planCandidates[]`
- [ ] `PlanCandidate` 스키마 — `planCandidateId` · `composition` · `grossBenefitWon` · `transitionCost{annualFeeDeltaWon, performanceRebuildCostWon, executionBurdenCostWon}` · `netBenefitWon` · `gatingResult` · `benefitDeltaWon` · `expiresAt`
- [ ] **금액 필드 직렬화 정책 적용** — 모든 `*Won` 필드를 정수로 제약(소수·부동소수점 거부). 자릿수 한계를 넘는 경우의 표현(문자열 직렬화 여부)을 결정하고 주석으로 근거를 남김
- [ ] 계약 타입으로부터 OpenAPI 스키마를 생성하거나, 수기 OpenAPI 문서와의 동기화 방법을 결정
- [ ] 계약 스냅샷 테스트 작성 — 스키마 변경 시 진단이 뜨도록
- [ ] `README` 또는 모듈 주석에 **"이 계약을 바꾸면 FE·Mock·테스트를 함께 갱신한다"** 를 명시

## 🧪 Acceptance Criteria (BDD/GWT)
Scenario 1: 정상 계산 요청·응답의 계약 검증
- Given: `futureSpendPlanIds`에 1건 이상이 담긴 요청 페이로드가 주어짐
- When: `CalculateRequest` 스키마로 파싱함
- Then: 검증을 통과하고, `CalculationResponse` 스키마는 `scenarios` 3건과 `defaultScenario: "AS_EXPECTED"`를 요구한다.

Scenario 2: 미래지출 0건 요청 거부
- Given: `futureSpendPlanIds: []` 인 요청 페이로드가 주어짐
- When: `CalculateRequest` 스키마로 파싱함
- Then: 검증에 실패하며, 실패 결과가 `CF-4001 FUTURE_SPEND_REQUIRED`로 매핑 가능한 형태를 갖는다. (REQ-EXC-001)

Scenario 3: "현재 조합 유지" 결론이 정상 응답으로 성립
- Given: `gatingResult: "KEEP_CURRENT"` 인 `PlanCandidate`가 담긴 응답 페이로드가 주어짐
- When: `CalculationResponse` 스키마로 파싱함
- Then: 검증을 통과하고 `error` 키가 없어도 유효하다. **"유지"는 오류가 아니다.** (ADR-01)

Scenario 4: 시나리오 개수 위반 거부
- Given: `scenarios`에 2건만 담긴 응답 페이로드가 주어짐
- When: `CalculationResponse` 스키마로 파싱함
- Then: 검증에 실패한다. 부분 결과를 계약 수준에서 차단한다. (REQ-EXC-005)

Scenario 5: 소수점 금액 거부
- Given: `netBenefitWon: 32000.5` 인 응답 페이로드가 주어짐
- When: `PlanCandidate` 스키마로 파싱함
- Then: 검증에 실패한다. 금액은 원 단위 정수만 허용한다.

## ⚙️ Technical & Non-Functional Constraints
- 정확성: 모든 `*Won` 필드는 **원 단위 정수**다. 부동소수점 표현을 허용하면 배분 합계 오차 ≤ 1원(REQ-FUNC-005)과 재계산 불일치 0건(REQ-NF-002)이 JSON 경계에서 깨진다.
- 보안: 응답 DTO에 **타인 식별 정보를 담을 수 있는 필드를 두지 않는다.** 오조회 0건(REQ-NF-004 · GR5)의 계약 수준 방어선이다.
- 성능: 이 계약을 쓰는 `POST /api/v1/calculate`는 p95 ≤ 5s(REQ-NF-001). 검증 로직이 응답 경로에서 병목이 되지 않도록 스키마 컴파일을 요청마다 반복하지 않는다.
- 아키텍처: 계약 모듈은 계산 로직·AI 모듈 어느 쪽도 import 하지 않는다. 의존성 경계 린트(IN-008) 대상이다.

## 🏁 Definition of Done (DoD)
- [ ] 모든 Acceptance Criteria를 충족하는가?
- [ ] 계약 스냅샷 테스트가 추가되었고 통과하는가?
- [ ] 배포 게이트 ①·②를 통과하는가? (C-TEC-007a)
- [ ] 의존성 경계 린트를 통과하는가? (ADR-02)
- [ ] Linter 경고가 없는가?
- [ ] SRS §6.1.3의 필드·규칙과 계약이 1:1로 대응하는가? (누락·추가 필드 0건)
- [ ] `python3 tools/verify_docs.py` 통과

## 🚧 Dependencies & Blockers
- Depends on: None
- Blocks: CT-002 · CT-003 · CT-004 · MK-001 · BE-033 · BE-034
```

---

## CT-002

```markdown
---
name: Feature Task
about: SRS 기반의 구체적인 개발 태스크 명세
title: "[Feature] CT-002: Evidence 도메인 DTO 정의 (근거 6항목 스키마)"
labels: 'feature, contract:api, epic:evidence, layer:ct, priority:p1'
assignees: ''
---

## 🎯 Summary
- 기능명: [CT-002] Evidence 도메인 DTO 정의
- 목적: 계산 근거 6항목의 타입을 고정해, **6개 미달을 계약 수준에서 표현 가능**하게 하고 AI 설명이 실패해도 근거가 그대로 노출되게 한다.

## 🔗 References (Spec & Context)
> 💡 AI Agent & Dev Note: 작업 시작 전 아래 문서를 반드시 먼저 Read/Evaluate 할 것.
- SRS 문서: [`§6.1.3 엔드포인트별 요청·응답 — GET /evidence`](#613-엔드포인트별-요청응답)
- 근거 공개 요구: [`§4.1 REQ-FUNC-006`](#41-기능-요구사항)
- 미달 거부 요구: [`§4.3 REQ-EXC-002`](#43-예외실패-처리-요구사항)
- 순서도: [`/docs/[설계 문서] CardFit (한글).md` §6.4 FC-04 근거 6항목 검증 게이트](#64-fc-04-근거-6항목-검증-게이트)
- 테스트 케이스: [`/docs/[테스트 명세서] CardFit (한글).md` TC-FUNC-006 · TC-EXC-002](#tc-func-006-계산-근거-공개-)
- 결정 근거: `ADR-02`(AI는 약관 요약·근거 설명만) · `GR3`(근거 미공개 노출 0건)

## ✅ Task Breakdown (실행 계획)
- [ ] `EvidenceItemType` enum 정의 — `PERFORMANCE_TIER` · `DISCOUNT_CAP` · `ANNUAL_FEE` · `EXCLUSION` · `BASE_DATE` · `UNREFLECTED` (SRS §6.1.3)
- [ ] `EvidenceItem` 스키마 — `type` · `label` · `value` · `sourceRuleVersion?`
- [ ] `EvidenceResponse` 스키마 — `items[]` · `unreflectedItems[]` · `ruleVersions[]` · `termsSummary?` · `rationale?` · `scopeNotice`
- [ ] **`items` 최소 길이 6 제약**을 스키마에 표현하고, 6종 `type`이 각각 최소 1회 등장하는지 검증 규칙 추가
- [ ] `unreflectedItems`를 **키 생략 불가**로 정의 — 없으면 빈 배열. 누락률 0% 표기(REQ-FUNC-006)를 계약이 강제한다
- [ ] `termsSummary` · `rationale`을 **nullable**로 정의하고, `null`이어도 응답 전체가 유효하도록 스키마를 구성
- [ ] `scopeNotice`를 필수 문자열로 정의 — "해지" 포함 결론일 때 값이 존재해야 함(REQ-FUNC-009)
- [ ] `ruleVersions[]`를 최소 1건으로 제약 — 적용 규칙 없이 근거가 성립하지 않음(REQ-NF-006)
- [ ] 6항목 미달 상황을 표현할 타입을 정의 — 성공 응답이 아니라 `CF-4221` 오류로 귀결됨을 타입 수준에서 분리
- [ ] 계약 스냅샷 테스트 작성 — 6항목 충족/미달 두 케이스

## 🧪 Acceptance Criteria (BDD/GWT)
Scenario 1: 근거 6항목 충족 응답의 계약 검증
- Given: `items`에 6종 `type`이 모두 담기고 `unreflectedItems`가 빈 배열인 페이로드가 주어짐
- When: `EvidenceResponse` 스키마로 파싱함
- Then: 검증을 통과한다.

Scenario 2: 6항목 미달 응답 거부
- Given: `items`에 5건만 담긴 페이로드가 주어짐
- When: `EvidenceResponse` 스키마로 파싱함
- Then: 검증에 실패하며, `CF-4221 EVIDENCE_INSUFFICIENT`로 매핑 가능한 형태를 갖는다. **근거 없는 결과를 계약이 통과시키지 않는다.** (REQ-EXC-002 · GR3)

Scenario 3: AI 설명 실패해도 응답이 유효
- Given: `termsSummary: null` · `rationale: null` 이고 `items` 6건이 담긴 페이로드가 주어짐
- When: `EvidenceResponse` 스키마로 파싱함
- Then: 검증을 통과한다. **AI는 보조 기능이므로 실패해도 근거는 노출된다.** (ADR-02)

Scenario 4: 미반영 항목 키 생략 거부
- Given: `unreflectedItems` 키가 아예 없는 페이로드가 주어짐
- When: `EvidenceResponse` 스키마로 파싱함
- Then: 검증에 실패한다. 빈 배열과 키 부재를 구분해 누락률 0% 표기를 강제한다.

## ⚙️ Technical & Non-Functional Constraints
- 성능: 이 계약을 쓰는 `GET /evidence`는 p95 ≤ 1s(REQ-NF-001).
- 정확성: `items` 최소 6건은 **계약 수준의 하드 제약**이다. 애플리케이션 검증에만 맡기면 GR3(근거 미공개 노출 0건)의 방어선이 한 겹뿐이 된다.
- 보안: `sourceRuleVersion`은 공개 약관 버전 식별자다. 사용자 식별 정보를 담지 않는다.
- 아키텍처: `termsSummary`·`rationale`은 AI 생성물이지만, 계약 모듈은 AI 모듈을 import 하지 않는다 — 문자열 필드로만 다룬다(ADR-02).

## 🏁 Definition of Done (DoD)
- [ ] 모든 Acceptance Criteria를 충족하는가?
- [ ] 6항목 충족/미달 두 케이스의 스냅샷 테스트가 통과하는가?
- [ ] 배포 게이트 ①·②를 통과하는가? (C-TEC-007a)
- [ ] 의존성 경계 린트를 통과하는가? (ADR-02)
- [ ] Linter 경고가 없는가?
- [ ] SRS §6.1.3의 Evidence 표와 계약이 1:1로 대응하는가?
- [ ] `python3 tools/verify_docs.py` 통과

## 🚧 Dependencies & Blockers
- Depends on: CT-001 (공통 응답 봉투 · 금액 직렬화 정책)
- Blocks: MK-002 · BE-021a · BE-035
```

---

## CT-003

```markdown
---
name: Feature Task
about: SRS 기반의 구체적인 개발 태스크 명세
title: "[Feature] CT-003: Outcome 도메인 DTO 정의"
labels: 'feature, contract:api, epic:tracking, layer:ct, priority:p2'
assignees: ''
---

## 🎯 Summary
- 기능명: [CT-003] Outcome 도메인 DTO 정의
- 목적: 완주 계측 요청·응답의 타입을 고정하되, **실행 개입을 유도하는 필드가 계약에 들어오지 못하게** 한다.

## 🔗 References (Spec & Context)
> 💡 AI Agent & Dev Note: 작업 시작 전 아래 문서를 반드시 먼저 Read/Evaluate 할 것.
- SRS 문서: [`§6.1.3 엔드포인트별 요청·응답 — POST /outcomes/{id}/completion`](#613-엔드포인트별-요청응답)
- 완주 계측 요구: [`§4.1 REQ-FUNC-010`](#41-기능-요구사항)
- 상태 전이: [`§6.5 상태 전이 규칙 — OutcomeLog`](#65-상태-전이-규칙)
- 시퀀스 다이어그램: [`/docs/[설계 문서] CardFit (한글).md` §5.8 SD-08 완주 계측](#58-sd-08-완주-계측--측정만-하고-개입하지-않는다)
- 결정 근거: `ADR-04`(실행은 스코프 밖) · `GR4`(실행 지원 오인 문구 0건)

## ✅ Task Breakdown (실행 계획)
- [ ] `OutcomeLogStatus` enum을 계약 타입으로 옮김 — `NOT_SENT` · `SENT` · `RESPONDED` · `NO_RESPONSE` (SRS §6.2)
- [ ] `CompletionRequest` 스키마 — `completed: boolean` · `incompleteReason?: string`
- [ ] `CompletionResponse` 스키마 — `recorded: boolean`
- [ ] **응답에 재시도·독려를 유도하는 필드를 두지 않는다** — `nextAction` · `retryUrl` · `reminderAt` 류의 필드 부재를 주석으로 명시하고 근거(ADR-04)를 남김
- [ ] `incompleteReason`의 용도를 **집계 전용**으로 주석에 명시 — 어떤 후속 액션도 트리거하지 않음
- [ ] 계약 스냅샷 테스트 작성

## 🧪 Acceptance Criteria (BDD/GWT)
Scenario 1: 완주 응답 기록
- Given: `completed: true` 인 요청 페이로드가 주어짐
- When: `CompletionRequest` 스키마로 파싱함
- Then: 검증을 통과하고, 응답은 `recorded: boolean` 단일 필드만 갖는다.

Scenario 2: 미완주 사유 수집
- Given: `completed: false` 와 `incompleteReason: "카드사 연결이 안 됐다"` 가 주어짐
- When: `CompletionRequest` 스키마로 파싱함
- Then: 검증을 통과한다. 사유는 저장되지만 계약 어디에도 후속 액션을 지시하는 필드가 없다. (ADR-04)

Scenario 3: 실행 개입 필드 부재 확인
- Given: 응답 스키마의 필드 목록이 주어짐
- When: 필드명을 검사함
- Then: `nextAction` · `retryUrl` · `reminderAt` 등 재시도·독려를 유도하는 필드가 **0개**다. (GR4)

## ⚙️ Technical & Non-Functional Constraints
- 스코프: 이 계약은 **측정 전용**이다. 실행 개입 엔드포인트는 존재하지 않으며, 계약에도 그 여지를 남기지 않는다(ADR-04).
- 보안: `incompleteReason`은 사용자 자유 입력이다. 저장·로깅 시 개인정보가 섞일 수 있으므로 마스킹 정책 대상임을 주석에 명시한다(REQ-NF-004).
- 계측: 무응답은 계약이 아니라 배치(BE-027a)가 `NO_RESPONSE`로 기록한다. 요청 스키마에 "무응답"을 표현하는 값을 두지 않는다.

## 🏁 Definition of Done (DoD)
- [ ] 모든 Acceptance Criteria를 충족하는가?
- [ ] 계약 스냅샷 테스트가 통과하는가?
- [ ] 배포 게이트 ①·②를 통과하는가? (C-TEC-007a)
- [ ] 의존성 경계 린트를 통과하는가? (ADR-02)
- [ ] Linter 경고가 없는가?
- [ ] 응답 스키마에 실행 개입을 유도하는 필드가 0개인가? (GR4)
- [ ] `python3 tools/verify_docs.py` 통과

## 🚧 Dependencies & Blockers
- Depends on: CT-001 (공통 응답 봉투)
- Blocks: MK-004 · BE-036
```

---

## CT-004

```markdown
---
name: Feature Task
about: SRS 기반의 구체적인 개발 태스크 명세
title: "[Feature] CT-004: 공통 에러 코드 체계 구현 (CF-4001 ~ CF-2001)"
labels: 'feature, contract:api, epic:api, layer:ct, priority:p0'
assignees: ''
---

## 🎯 Summary
- 기능명: [CT-004] 공통 에러 코드 체계 구현
- 목적: 예외 6건에 고유 코드를 부여해, **같은 HTTP 상태를 쓰는 서로 다른 거부를 클라이언트가 분기**할 수 있게 한다.

## 🔗 References (Spec & Context)
> 💡 AI Agent & Dev Note: 작업 시작 전 아래 문서를 반드시 먼저 Read/Evaluate 할 것.
- SRS 문서: [`§6.1.2 에러 코드 체계`](#612-에러-코드-체계)
- 공통 응답 봉투: [`§6.1.1 공통 응답 봉투`](#611-공통-응답-봉투)
- 예외 요구사항: [`§4.3 예외·실패 처리 요구사항 — REQ-EXC-001~006`](#43-예외실패-처리-요구사항)
- 예외 분기 순서도: [`§4.3 그림 — 어떤 상황에서 결과를 주지 않는가`](#43-예외실패-처리-요구사항)
- 테스트 케이스: [`/docs/[테스트 명세서] CardFit (한글).md` TC-EXC-001 ~ TC-EXC-006](#3-예외-테스트--tc-exc-001--006)
- Guardrail: `GR3`(근거 미공개 0건 → CF-4221) · `GR5`(오조회 0건 → CF-4030)

## ✅ Task Breakdown (실행 계획)
- [ ] `ErrorCode` enum 정의 — SRS §6.1.2의 7건을 그대로 옮김 (`CF-4001` `CF-4002` `CF-4030` `CF-4100` `CF-4221` `CF-4222` `CF-2001`)
- [ ] 코드 ↔ HTTP 상태 매핑 테이블 구현 — `400` `403` `410` `422` `200`
- [ ] 코드 ↔ 근거 요구사항 매핑 구현 — `error.requirement` 필드에 `REQ-EXC-001` 등을 채움
- [ ] **`CF-2001`을 `warning` 계열로 분리** — `error`가 아니라 `warning` 키에 실린다. 타입 수준에서 두 계열을 구분
- [ ] `ApiError` 스키마 — `code` · `message` · `requirement`
- [ ] `ApiWarning` 스키마 — `code` · `message` · `baseDate`(필수, `CF-2001`의 기준일)
- [ ] **`CF-4030` 응답 생성 시 타인 정보 차단** — 메시지 템플릿에 어떤 식별자도 보간하지 않도록 타입·헬퍼를 설계
- [ ] 사용자 노출 메시지를 **금지어 사전(`tools/prohibited-terms.json`)에 저촉하지 않게** 작성하고, 정적 스캔 대상에 포함
- [ ] `warning`과 `data`가 **동시에 존재 가능**함을 타입으로 표현 (`CF-2001`은 계산 성공과 함께 온다)
- [ ] 7건 전체의 매핑 테이블 테스트 작성 — 코드·상태·요구사항 3열 대조

## 🧪 Acceptance Criteria (BDD/GWT)
Scenario 1: 같은 400을 쓰는 두 거부의 분기
- Given: `CF-4001`(미래 입력 0건) 응답과 `CF-4002`(동의 실효) 응답이 각각 주어짐
- When: 클라이언트가 `error.code`로 분기함
- Then: 두 응답 모두 HTTP `400`이지만 서로 다른 코드로 구분되며, 각각 `REQ-EXC-001` · `REQ-EXC-004`를 `requirement`로 갖는다.

Scenario 2: 마이데이터 장애는 오류가 아니다
- Given: 마이데이터 장애로 최근 확인 스냅샷을 사용한 계산 결과가 주어짐
- When: 응답 봉투를 파싱함
- Then: HTTP `200`이고 `data`가 존재하며, `CF-2001`은 `error`가 아니라 **`warning`** 키에 실리고 `baseDate`를 포함한다. (REQ-EXC-003)

Scenario 3: 오조회 응답에 타인 정보 부재
- Given: 응답 주체와 로그인 사용자가 불일치해 `CF-4030`이 발생함
- When: 응답 페이로드를 검사함
- Then: `code`와 `message`만 존재하고, **타인의 어떤 식별자·데이터도 포함되지 않는다.** (REQ-NF-004 · GR5)

Scenario 4: 근거 미달 응답에 data 키 부재
- Given: 근거 항목이 6개 미달이어서 `CF-4221`이 발생함
- When: 응답 봉투를 파싱함
- Then: `error`만 존재하고 `data` 키가 **없다**(`null`이 아니라 키 자체가 부재). (REQ-EXC-002 · GR3)

Scenario 5: 매핑 누락 검출
- Given: `ErrorCode` enum의 전체 값이 주어짐
- When: 코드 ↔ HTTP 상태 ↔ 요구사항 매핑 테이블을 검사함
- Then: 7건 모두 세 열이 채워져 있고, SRS §6.1.2 표와 일치한다.

## ⚙️ Technical & Non-Functional Constraints
- 보안: `CF-4030` 메시지에 **타인의 어떤 정보도 보간하지 않는다.** 오조회는 GR5 위반으로 즉시 중단·신고 대상이므로, 응답이 정보 유출 경로가 되어서는 안 된다(REQ-NF-004).
- 규제: 모든 사용자 노출 메시지는 **금지어 정적 스캔(배포 게이트 ②)** 대상이다. 실행 대행·보장 표현이 섞이면 GR4 위반으로 배포가 차단된다.
- 정합성: 코드 표는 SRS §6.1.2가 정본이다. 코드를 추가·변경하려면 **SRS를 먼저 고친다.**
- 관측: 각 코드의 발생 건수는 Guardrail 감시 대상이다 — `CF-4221`은 GR3, `CF-4030`은 GR5로 집계된다(REQ-NF-009).

## 🏁 Definition of Done (DoD)
- [ ] 모든 Acceptance Criteria를 충족하는가?
- [ ] 매핑 테이블 테스트 7건이 통과하는가?
- [ ] 배포 게이트 ①·②를 통과하는가? (C-TEC-007a) — 특히 메시지가 금지어 스캔을 통과하는가
- [ ] 의존성 경계 린트를 통과하는가? (ADR-02)
- [ ] Linter 경고가 없는가?
- [ ] SRS §6.1.2의 7건과 구현이 1:1로 대응하는가? (누락·추가 0건)
- [ ] `python3 tools/verify_docs.py` 통과

## 🚧 Dependencies & Blockers
- Depends on: CT-001 (공통 응답 봉투 타입)
- Blocks: MK-003 · BE-021b · BE-033
```

---

## 부록 — 이 배치를 끝낸 뒤 열리는 것

| 즉시 착수 가능 | 근거 |
| :---: | --- |
| **MK-001 ~ MK-004** | 계약이 확정되면 Mock을 만들 대상이 생긴다 |
| BE-021a · BE-035 | CT-002 완료 시 |
| BE-033 · BE-034 | CT-001 · CT-004 완료 시 |

**Mock 4건이 열리는 것이 이 배치의 실질적 효과다.** Mock이 나오면 FE 24건 중 23건의 백엔드 직렬 의존이 풀린다(평가서 0-0절 실측: 18/24 → 1/24).

---

*근거 문서: `../[태스크 리스트] CardFit.md` (TASK-CARDFIT-001 v1.1)*
