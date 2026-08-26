---
name: grill-it
description: 사용자가 아니라 "문제"를 함께 굽는다. 착수 전에 사용자가 지정한 참조 범위·관심 방향 안에서 미해소 결정 토픽 전체를 먼저 추출해 가시화하고, 의존 순서대로 한 토픽씩 권장안과 함께 해소하며, 해소되는 즉시 설계문서(PRD/SRS/Tasks/Issues)와 에이전트 하네스(rules/AGENTS.md/CLAUDE.md)에 반영하고 재개 가능한 Grill Ledger에 기록한다.
when_to_use: Use when the user wants to de-risk a plan/design before building, clear ambiguities up front, mentions "grill-it", "grill the problem", "문제를 굽자", "착수 전 모호함 정리", "결정 사항 하네스에 반영", or wants a scoped, resumable decision-clearing session that updates design docs and the agent harness.
---

# Grill-It Operating Rules

## 역할

이 스킬은 **사용자를 grilling 하지 않는다.** 사용자와 **함께 "문제"를 grilling** 한다. 구워지는 대상은 사람이 아니라 문제이고, 문제가 잘 구워지면 잘 차려진 결과물(정합된 설계문서와 하네스)이 함께 나온다.

구현에 착수하기 전에, 지정된 범위 안에서 **미해소 결정 토픽**을 모두 끄집어내 가시화하고, 하나씩 함께 해소하며, **해소되는 즉시 설계문서와 에이전트 하네스에 반영**한다.

```
사용자의 범위·방향 → [grill-it] → 토픽 원장 추출(가시화) → 한 토픽씩 해소 → 매 해소 즉시 문서·하네스 반영 → 모든 토픽 RESOLVED
```

핵심 전환:

- grill-me: 에이전트가 **나(사용자)** 를 추궁한다 → 피로·이탈, 결과물 미잔존
- grill-it: 에이전트가 **나와 함께 문제** 를 굽는다 → 범위가 좁고, 진척이 보이고, 결과물이 남고, 재개 가능하고, 하네스에 즉시 반영된다

---

# 기본 원칙

1. 굽는 대상은 **문제**다. 사용자를 시험하지 말고 결정의 공동 소유자로 대한다. 모든 질문에는 **권장안 + 근거 한 줄**을 함께 제시해, 사용자가 "생성"이 아니라 "확인·교정"만으로 진행하게 한다 (저피로 기본 경로).
2. **범위 밖을 스캔하지 않는다.** 참조 범위·관심 방향이 정해지기 전에는 전체 워크스페이스를 훑지 않는다. 탐색은 현재 토픽 해소에 필요한 만큼만 한다.
3. **착수 전 전체 토픽을 먼저 가시화한다.** 무작정 질문을 시작하지 않는다. 먼저 범위 안의 미해소 결정 토픽 리스트를 추출해 개수·분류(CORE/MINOR)·의존 순서와 함께 제시한다. 사용자는 처음부터 "앞으로 몇 번 문답하는지"를 안다.
4. **한 번에 하나씩.** 의존 순서대로 한 토픽씩 해소한다. 한 토픽이 해소되기 전에는 다음으로 넘어가지 않는다.
5. **결정형 질문은 선택형 UI로 묻는다.** Agent Client Protocol의 `AskUserQuestion` 등 클라이언트 질문 UI가 있으면 평문 질문으로 끝내지 말고 선택형 UI를 띄운다. 권장안을 첫 옵션으로 두고, 의존 순서상 한 번에 한 토픽만 묻는다. 질문 UI가 없는 환경에서만 텍스트 `[질문]`으로 fallback한다.
6. **해소 즉시 영속화.** 한 토픽이 결정되면 다음 질문으로 넘어가기 전에 (a) 관련 설계문서와 (b) 에이전트 하네스(규칙·스킬·서브에이전트·워크플로/명령·훅 등 결정 성격에 맞는 계층)를 수립·수정하고 (c) Grill Ledger에 RESOLVED로 기록한다. 결정을 메모리에만 두지 않는다.
7. **언제든 멈추고 재개 가능.** Grill Ledger가 진척 상태를 보존하므로, 세션을 중간에 끝내도 다음에 첫 UNRESOLVED 토픽부터 이어간다.
8. 출력에 분석·이론·레퍼런스를 넣지 않는다. 행동(추출·질문·반영·기록)만 수행한다.

---

# Three Pillars (필수 통과 기준)

```
Boundedness   — 참조 범위와 관심 방향이 명시되어 있고, 탐색이 그 범위로 한정되는가?
Visibility    — 착수 전 미해소 토픽 전체 리스트가 추출·제시되고, 매 턴 진척(해소/잔여)이 보이는가?
Persistence   — 각 토픽이 해소되는 즉시 설계문서 + 하네스에 반영되고 Grill Ledger에 기록되는가?
```

| 기둥 | 통과 기준 | 위반 시 |
|------|-----------|---------|
| Boundedness | 참조 범위(A) + 관심 방향(B)이 확정됨 | grill loop 진입 금지 → 먼저 질문 |
| Visibility | Grill Ledger에 토픽 전체가 열거되고 카운터 노출 | 질문 시작 금지 → 먼저 토픽 추출 |
| Persistence | 직전 RESOLVED 토픽이 문서·하네스·원장에 반영됨 | 다음 토픽으로 진행 금지 → 먼저 반영 |

세 기둥을 동시에 만족하지 못하면 다음 단계로 진행하지 않는다.

---

# Intake (착수 입력)

`/grill-it` 호출 시 다음 4가지를 확인한다. 이미 제공된 항목은 다시 묻지 않는다.

```
A. 참조 범위        — 어떤 문서/디렉터리/모듈을 근거로 삼는가? (예: PRD, SRS, Tasks, Issues 등 핵심 설계문서)
B. 핵심 관심 방향   — 무엇의 모호함을 굽고 싶은가? (예: UX flow, UI 유형, 데이터 스키마·흐름·저장 방침, 기술스택·세부 설계 확정 여부)
C. 작업 범위·완료조건 — 어디까지 해소하면 끝인가? (기본: 관심 방향의 미해소 토픽이 전부 RESOLVED 될 때까지)
D. 작업 결과 OUTPUT — 결정이 반영될 대상. (기본: 핵심 설계문서 + 현재 프로젝트의 에이전트 하네스 전반)
```

- A·B가 비면 grill loop를 시작하지 않고 먼저 묻는다.
- C·D가 비면 위 기본값을 제안한 뒤 확인받는다.

---

# OUTPUT: 무엇이 "구워지는가"

grill-it의 산출물은 대화가 아니라 **남는 것**이다.

### 1. Grill Ledger (토픽 원장)

결정 토픽의 단일 진척 원장. 기본 경로 `docs/grill/GRILL_LEDGER.md` (없으면 사용자와 합의해 생성). 상단에 grep 가능한 카운터 한 줄을 유지한다.

```
RESOLVED: 0 / TOTAL: m
- [ ] T1 | CORE  | <한 줄 토픽>            | depends:-     | status:UNRESOLVED
- [ ] T2 | CORE  | <한 줄 토픽>            | depends:T1    | status:UNRESOLVED
- [ ] T3 | MINOR | <한 줄 토픽>            | depends:-     | status:UNRESOLVED
```

해소된 토픽은 한 행에 결정과 반영 결과를 함께 기록한다.

```
- [x] T1 | CORE | <한 줄 토픽> | status:RESOLVED | decision:<한 줄 결정> | applied:<수정한 파일/하네스>
```

### 2. 설계문서 반영

PRD/SRS/Tasks/Issues 등 관련 문서를 결정대로 수정한다.

### 3. 하네스 반영 (에이전트 제어면 전체)

"하네스"는 규칙 파일에 그치지 않는다. **에이전트의 동작을 제어하는 모든 산출물**을 뜻한다. 결정의 성격에 맞는 하네스 계층을 골라, 한 번 내린 결정이 이후 작업에서 자동으로 지켜지도록 수립·갱신한다.

| 하네스 계층 | 무엇인가 | 이런 결정일 때 수립/갱신 |
|------------|----------|--------------------------|
| Rules | 항상 적용되는 행동 규칙·정책 | 지속 적용할 제약 (예: "기본 저장소는 Postgres") |
| Skills | 반복 가능한 역량(절차) | 반복 수행할 작업 패턴이 정해졌을 때 |
| Subagents / Agents | 위임 역할·페르소나 | 특정 역할을 분리·위임하기로 했을 때 |
| Workflows / Commands | 다단계 절차·슬래시 명령 | 정형화된 작업 순서가 확정됐을 때 |
| Hooks | 이벤트 트리거 자동화 | 특정 시점에 자동 실행할 동작이 정해졌을 때 |
| MCP / Settings | 외부 연동·도구 설정 | 외부 서비스·도구 사용 방침이 확정됐을 때 |

도구별 위치:

| 도구 | 하네스 위치 |
|------|-------------|
| 공통 | `AGENTS.md`, PRD/SRS/Tasks/Issues |
| Cursor | `.cursor/rules/*.mdc`, `.cursor/skills/*/SKILL.md`, `.cursor/commands/*`, `.cursor/hooks/`·`hooks.json`, `AGENTS.md` |
| Claude Code | `CLAUDE.md`, `.claude/skills/*/SKILL.md`, `.claude/agents/*`, `.claude/commands/*`, `.claude/settings.json` |
| Codex | `AGENTS.md`, `.agents/skills/*/SKILL.md`, `.agents/` 설정 |

- **CORE 결정**(아키텍처·보안·외부 의존·데이터 모델·핵심 UX 계약)은 반드시 설계문서와 하네스에 반영한다. 결정이 **반복 동작·역할·절차·자동화**를 함의하면 규칙 한 줄에 그치지 말고 그에 맞는 **skill·subagent·workflow/command·hook**까지 수립한다.
- **MINOR 결정**(네이밍·디렉터리·로그 포맷·UI 디테일)은 원장 기록 + 관련 문서/규칙 한 줄 반영으로 충분하다.
- 어떤 하네스 계층을 수립·갱신했는지는 Grill Ledger의 `applied:` 필드에 기록한다.

---

# Workflow

## Step 0 — Intake & Scope Lock

A~D를 확인한다. A·B 누락 시 질문한다. 범위 밖 전체 스캔을 하지 않는다.

## Step 1 — Topic Extraction (추출 → 가시화)

참조 범위 안만 읽어, 관심 방향에 해당하는 **미해소 결정 토픽**을 전부 추출한다. 각 토픽을 CORE/MINOR로 분류하고 의존 관계로 정렬해 **전체 리스트**를 한 코드블록(Grill Ledger)으로 제시한다. 사용자에게 `총 m개 (CORE x / MINOR y)`를 보여준다.

- 미해소 토픽이 0개면 모호함 없음을 보고하고 종료한다. **억지로 질문을 만들지 않는다.**
- 토픽 추출 직후, 같은 응답에서 첫 토픽(Step 2)을 연다.

## Step 2 — Grill the Topic (한 토픽씩, 권장안 동반)

의존 순서상 첫 UNRESOLVED 토픽을 연다. 출력:

- 진척: `RESOLVED n / TOTAL m` + 현재 토픽 ID·한 줄
- 선택지 2~4개 (각 trade-off 한 줄)
- **권장안 + 근거 한 줄**
- 사용자에게 단일 질문 1개 (권장안 확정 또는 다른 선택)

질문 전달은 가능한 경우 Agent Client Protocol의 `AskUserQuestion` 또는 동등한 선택형 질문 UI를 사용한다. UI 옵션은 권장안을 맨 위에 두고 2~4개의 상호배타 선택지로 구성하며, 사용자가 답하기 쉽게 각 옵션에 trade-off를 한 줄로 붙인다. 평문 `[질문]`은 해당 UI를 사용할 수 없는 클라이언트에서만 fallback으로 쓴다.

한 번에 한 토픽만 묻는다.

## Step 3 — Resolve & Persist (해소 즉시 반영)

사용자 답으로 결정이 확정되면, **다음 토픽으로 넘어가기 전에**:

1. 관련 설계문서 수정
2. 하네스 반영 (CORE면 필수)
3. Grill Ledger에서 해당 토픽 `status:RESOLVED` + `decision:` + `applied:` 기록, 상단 카운터 +1
4. `[반영 완료]` 한 줄로 무엇을 어디에 반영했는지 사용자에게 surface

## Step 4 — Advance or Stop

다음 UNRESOLVED 토픽으로 이동(Step 2). 다음 중 하나면 종료:

- 모든 토픽 RESOLVED → STOP: ALL_RESOLVED
- 사용자가 중단 요청 → STOP: USER_PAUSED (잔여 토픽이 원장에 남아 재개 가능)
- (선택) 사전 합의한 토픽/턴 budget 도달 → STOP: BUDGET

## Step 5 — Resume (재개)

재호출 시 Grill Ledger를 읽어 첫 UNRESOLVED 토픽부터 Step 2로 이어간다. 이미 RESOLVED인 토픽은 다시 묻지 않는다.

## Step 6 — Closeout (종료 보고)

종료 시 Grill Ledger 상단 카운터와 STOP 사유를 한 번 보여주고, 이번 세션에 반영된 설계문서·하네스 변경 목록을 요약한다 (잘 차려진 결과물).

---

# 협업 프레이밍 규칙 (사용자를 굽지 않기)

- 추궁·시험 톤 금지. "이 **문제**의 이 지점이 아직 안 정해졌다"처럼 **문제를 주어**로 말한다.
- 모든 질문에 권장안을 먼저 제시하고 "이대로 갈까요?"를 기본 경로로 둔다. 결정형 질문은 가능한 경우 선택형 UI로 띄워 사용자가 동의 또는 교정만 하면 되게 한다.
- 사용자가 "권장안대로"라고 하면 즉시 Step 3로 넘어간다.
- 한 응답에 여러 토픽을 몰아 묻지 않는다 (피로 유발).

---

# Refusal & 보충

| 상황 | 처리 |
|------|------|
| 참조 범위(A) 없음 | grill 시작 안 함 — 어떤 문서/디렉터리를 근거로 삼을지 먼저 질문 |
| 관심 방향(B) 없음 | grill 시작 안 함 — 무엇의 모호함을 굽고 싶은지 질문 |
| 미해소 토픽 0개 | 모호함 없음 보고 + 종료 (억지 질문 생성 금지) |
| OUTPUT 대상(D) 불명 | 기본값(핵심 설계문서 + 하네스) 제안 후 확인 |
| 범위 밖 전체 스캔 요구 | 비용·정확도 경고 + 범위 한정 권장 |
| RESOLVED 미반영 상태로 다음 토픽 요구 | 진행 보류 — 직전 결정의 문서·하네스 반영을 먼저 완료 |

---

# 출력 형식 (per-turn)

매 응답은 `---` 가로줄로 영역을 분리한다.

결정형 질문은 가능한 경우 Agent Client Protocol의 `AskUserQuestion` 등 선택형 UI로 전달한다. 아래의 `[질문]` 텍스트는 질문 UI를 사용할 수 없는 환경에서만 쓰는 fallback 형식이다.

### 토픽 추출 턴

````
**[범위 확인]** 참조: … / 방향: … / 완료조건: … / OUTPUT 대상: …

---

**[토픽 원장 — 총 m개 (CORE x / MINOR y)]**

```markdown
RESOLVED: 0 / TOTAL: m
- [ ] T1 | CORE  | … | depends:-  | status:UNRESOLVED
- [ ] T2 | CORE  | … | depends:T1 | status:UNRESOLVED
```

---

**[진척]** RESOLVED 0 / TOTAL m · 현재 토픽: T1 …

**[선택지]**
- A) … — trade-off
- B) … — trade-off

**[권장]** B) — 근거 한 줄

**[질문 UI]** AskUserQuestion으로 B(권장)를 첫 옵션에 두고, 나머지 선택지를 이어서 제시
**[질문 fallback]** B로 확정할까요, 아니면 다른 방향이 있나요?
````

### 해소·반영 턴 (사용자 답변 직후)

````
**[반영 완료]** T1 → decision: 한 줄 결정
- 설계문서: docs/PRD.md §X 갱신
- 하네스: CLAUDE.md 반영
- 원장: GRILL_LEDGER.md (RESOLVED 1 / TOTAL m)

---

**[진척]** RESOLVED 1 / TOTAL m · 현재 토픽: T2 …
**[선택지]** …
**[권장]** …
**[질문 UI]** AskUserQuestion(권장안 첫 옵션)
````

---

# 시나리오 예시 (요약)

**User:** "PRD, SRS 기준으로 착수 전에 데이터 스키마·저장 방침이 모호한 부분 정리해줘. 결정은 설계문서랑 하네스에 반영하고."

1. **Intake**: A=`docs/PRD.md`, `docs/SRS.md` / B=데이터 스키마·흐름·저장 방침 / C=관심 방향 미해소 토픽 전부 / D=설계문서 + 하네스. → 확정.
2. **Topic Extraction**: 범위만 읽어 토픽 추출 후 원장 제시.

```markdown
RESOLVED: 0 / TOTAL: 3
- [ ] T1 | CORE  | 사용자 데이터 저장소 선택(관계형 vs 문서형) | depends:-  | status:UNRESOLVED
- [ ] T2 | CORE  | 개인정보 보존 기간·삭제 정책            | depends:T1 | status:UNRESOLVED
- [ ] T3 | MINOR | 테이블/컬렉션 네이밍 규칙               | depends:T1 | status:UNRESOLVED
```

3. **Grill T1**: 선택지(Postgres / DynamoDB …) + 권장안(관계형 — 강한 관계·트랜잭션 필요) + AskUserQuestion 선택형 UI(권장안 첫 옵션)로 단일 질문.
4. **Resolve T1**: 사용자 "권장안대로" → `docs/SRS.md` 데이터 섹션 갱신 + `CLAUDE.md`에 "기본 저장소 = Postgres" 반영 + 원장 `RESOLVED 1 / TOTAL 3`. → `[반영 완료]` 후 T2로.
5. 모든 토픽 RESOLVED → Closeout: 카운터 + 변경 목록 요약.
