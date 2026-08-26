# CardFit — 프로젝트 컨텍스트

**이 파일은 Claude Code가 작업 시작 시 자동 로드한다.** 항상 적용되는 규칙만 둔다. 도메인 지식은 `.claude/agents/`, 절차는 `.claude/commands/`, 외부 기술 레퍼런스는 `.claude/skills/`에 있다.

---

## 1. 이 프로젝트가 만드는 것

**보유 카드 조합을 재설계해 주는 서비스다.** 미래 지출 계획을 입력받아 순혜택을 계산하고, **바꿀 만하지 않으면 "그대로 두세요"를 결론으로 반환한다.**

| 축 | 내용 |
| --- | --- |
| 북극성 지표 | 조합안 선택률 ≥ 40% |
| 핵심 차별점 | **"유지"도 정답이다**(ADR-01) — 임계 미달 시 변경을 제안하지 않는다 |
| 범위 밖 | **실행 대행.** 신청·해지는 카드사에서 직접 한다 |
| 현재 단계 | 태스크 59건 이슈 발급 완료 · 구현 착수 전 |

**근거 문서 — 코드를 쓰기 전에 해당 문서를 읽는다.**

| 문서 | 언제 읽나 |
| --- | --- |
| `docs/[SRS 문서] CardFit (한글).md` | 요구사항·제약·API·스키마. **모든 태스크의 근거** |
| `docs/[계산 명세서] CardFit (한글).md` | 계산 순서·전환비용·임계값. **계산 관련 값의 유일한 정본** |
| `docs/[픽스처 데이터 명세] CardFit (한글).md` | 픽스처 모드 경계·시연 데이터 |
| `docs/[설계 문서] CardFit (한글).md` | 컴포넌트·클래스·시퀀스 |
| `docs/[테스트 명세서] CardFit (한글).md` | 판정 SLO. **AC를 새로 만들지 않는다** |
| `docs/tasks/<ID>.md` | 태스크 1건의 실행 계획·AC·DoD |
| `docs/[개발 실행 총괄] CardFit (한글).md` | 의존성·일정·트랙 |

---

## 2. 기술 스택 (C-TEC-001~007)

**제약이지 선택지가 아니다.** SRS 1.5가 고정한 값이며, 바꾸려면 SRS를 먼저 고쳐야 한다.

| 영역 | 값 | 근거 |
| --- | --- | :---: |
| 프레임워크 | **Next.js App Router** 단일 풀스택. 프론트·백엔드를 분리하지 않는다 | C-TEC-001 |
| 서버 로직 | **Server Actions 또는 Route Handlers.** 별도 백엔드 서버를 두지 않는다 | C-TEC-002 |
| DB | **Prisma + Supabase(PostgreSQL).** Prisma 스키마가 정본, SRS 6.4 DDL은 생성물 | C-TEC-003 |
| UI | **Tailwind + shadcn/ui** | C-TEC-004 |
| AI | **Vercel AI SDK.** 기본 Google Gemini, **환경변수만으로 모델 교체** | C-TEC-005·006 |
| 배포 | **Vercel.** Git Push 자동화, 파이프라인 미구성 | C-TEC-007 |
| 예외 | **배포 전 검증 게이트 1개만 허용** — 경계값 회귀 + 금지어 스캔 | C-TEC-007a |

**언어는 TypeScript strict.** 금액은 전 경로에서 원 단위 정수(`BigInt`)다.

---

## 3. 절대 어기면 안 되는 것 — 불변식 6

**이것을 어기면 서비스가 중단된다.** 상세는 `.agents/rules/004-invariants.md`.

| # | 불변식 | 어기면 |
| :---: | --- | --- |
| **I1** | **AI는 계산 영역을 호출하지 않는다** — 결과를 인자로만 받는다 | ADR-02 위반. 재계산 불일치의 첫 번째 용의자 |
| **I2** | **금액은 원 단위 정수다** — 계산 경로에 부동소수를 두지 않는다 | 배분 합계 오차·재계산 불일치 (GR1) |
| **I3** | **계산 경로에 비결정론을 두지 않는다** — `Math.random()`·`new Date()`·해시 순회 금지 | 재계산 불일치 0건(REQ-NF-002) 위반 |
| **I4** | **임계 미달이면 변경을 제안하지 않는다** — 절대 월 3,000원 **그리고** 상대 10% | **GR2 위반 = 즉시 서비스 중단** |
| **I5** | **근거 6항목 미달이면 응답을 거부한다** — AI 설명은 게이트 뒤에 있다 | **GR3 위반** |
| **I6** | **응답 주체 ≠ 로그인 사용자면 즉시 차단한다** | **GR5 위반 = 컴플라이언스가 PM을 우회해 단독 중단** |

> **"유지" 결론은 실패가 아니다.** `KEEP_CURRENT`는 `200`으로 반환하며 `error` 키를 두지 않는다. 화면에서도 실패색·재시도 유도를 쓰지 않는다.

---

## 4. 개발 규칙

### 작업 시작
1. `docs/tasks/<ID>.md`의 **Depends on이 전건 완료**됐는지 확인한다
2. References에 적힌 문서를 **먼저 읽는다**
3. AC의 판정 기준값이 **명세에서 온 것**인지 확인한다 — 임의 값이면 잘못 읽은 것이다

### 코드
- **AC를 새로 만들지 않는다.** STD에 판정 SLO 27건이 이미 있다
- **계산 값은 CALC에서 인용한다.** SRS 4.1.0은 "정해야 했다"는 기록이고 값은 계산 명세에 있다
- 주석은 **왜**를 적는다. 무엇은 코드로 표현한다
- 픽스처 모드(`CARDFIT_DATA_MODE=fixture`)에서 **외부 호출 0회**로 동작해야 한다

### 완료
공통 DoD 8항목은 각 `docs/tasks/<ID>.md`에 있다. 그중 셋은 이 프로젝트 고유다.
- 배포 게이트 ①② 통과 (C-TEC-007a)
- 의존성 경계 린트 통과 (I1)
- 픽스처 모드 외부 호출 0회

### 검증
```bash
python3 tools/verify_docs.py          # 문서 정합성 110항목
python3 tools/generate_fixtures.py    # 픽스처 + 참조 계산기 대조
```

---

## 5. 라우팅

### 서브에이전트 (`.claude/agents/`)
| 에이전트 | 사용 시점 |
| --- | --- |
| `nextjs-server` | Route Handlers · Server Actions · API 계약 · 인증 |
| `prisma-supabase` | 스키마·마이그레이션·RLS·감사 로그 |
| `calc-engine` | 계산 파이프라인 · 게이팅 · 조합·배분 · 결정론 |
| `fixture-mode` | 어댑터 경계 · 시드 적재 · 캐시↔실호출 전환 |
| `compliance-guardrail` | 금지어 스캔 · 경계 고지 · Guardrail 5건 · 배포 게이트 |
| `frontend-shadcn` | 화면 구현 · 상태 · 계측 이벤트 |

### 슬래시 커맨드 (`.claude/commands/`)
| 커맨드 | 목적 |
| --- | --- |
| `/task-start` | 이슈 하나를 착수 조건 점검부터 시작 |
| `/verify` | 문서·픽스처·게이트 전체 검증 |
| `/fix-error` | 에러 7단계 구조화 진단 |
| `/gitflow-commit` | 저장소 관례에 맞춘 커밋·PR |
| `/setup-env` | 로컬 개발환경 기동 |

### 외부 스킬 (`.claude/skills/`)

| 묶음 | 스킬 | 언제 |
| --- | --- | --- |
| 스택 | `prisma-client-api` · `prisma-database-setup` · `supabase-postgres-best-practices` · `deploy-to-vercel` · `react-best-practices` | DB·배포·화면 작업 시 |
| 엔지니어링 | `tdd` · `code-review` · `diagnosing-bugs` | 테스트·리뷰·진단 |
| 작업 방식 | `grill-it` · `goal-setting` · `review-merge` · `merge-review` | 결정 해소 · 목표 설계 · PR 리뷰·머지 |

**PR 묶음의 성격에 따라 `review-merge`와 `merge-review`를 갈라 쓴다** — 독립 PR은 리뷰 후 머지, 응집 PR 묶음은 머지 후 통합 리뷰다.

채택·미채택 근거는 `docs/[하네스 구성] CardFit (한글).md`에 있다.

---

## 6. 새 규칙을 추가할 때

| 성격 | 위치 |
| --- | --- |
| 항상 적용 | 이 파일 또는 `.agents/rules/` |
| 도메인 지식 | `.claude/agents/` |
| 절차·프로세스 | `.claude/commands/` |
| 외부 기술 레퍼런스 | `.claude/skills/` (출처 명시) |
