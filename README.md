# cardfit-prd-to-srs

**CardFit PRD**를 **SRS 문서**로 변환하고, 그 SRS에서 설계·테스트·태스크 산출물을 파생하는 작업 저장소입니다.

---

## 1. 작업 목표

### 1.1 하는 일

> **기준 템플릿은 `[SRS 문서] AD-Core-Platform (한글).md` 하나입니다.**

`cardfit-prd-v1_0.md`에 담긴 내용을, 예시 SRS 문서가 이미 쓰고 있는 **섹션 구성·표 스키마·ID 체계·서술 톤**으로 옮겨 적습니다. 도메인만 다를 뿐(광고 플랫폼 → 카드 조합 최적화), 문서의 **뼈대는 예시 문서를 그대로 따릅니다.**

### 1.2 하지 않는 일

**ISO/IEC/IEEE 29148:2018을 전부 만족하는 풀 스펙 SRS를 쓰는 것이 목표가 아닙니다.**

표준이 요구하는 전체 섹션을 빠짐없이 채우는 방향으로 문서를 부풀리지 않습니다. 예시 SRS가 다루지 않은 영역은 아래 확장 규칙에 해당하지 않는 한 **쓰지 않습니다.**

### 1.3 확장 규칙

PRD에는 예시 SRS의 7개 섹션 어디에도 들어가지 않는 내용이 있습니다. 버리지 않되 임의의 형식으로 덧붙이지도 않습니다.

| 상황 | 처리 |
| --- | --- |
| 예시 SRS에 대응 섹션이 있음 | 예시 포맷 그대로 채움 |
| 예시 SRS에 대응 섹션이 없음 | **그 부분만** 29148 구성에 따라 섹션 신설 |
| PRD에 없는데 예시 SRS에는 있음 | 억지로 만들지 않고 `TBD` 표기 |

확장으로 신설한 섹션은 **어느 표준 조항을 근거로 추가했는지** 문서 안에 밝힙니다. 확장은 **최소 단위**로 합니다.

---

## 2. 파일 구조

```
.
├── README.md
├── cardfit-prd-v1_0.md                       ← 입력 PRD
├── [SRS 문서] AD-Core-Platform (한글).md       ← 양식 기준 템플릿
├── 29148-2018-ISOIECIEEE.pdf                 ← 준거 표준 (저장소 미포함)
├── docs/                                     ← 산출물
│   ├── [SRS 문서] CardFit (한글).md
│   ├── [SRS 이해 가이드] CardFit (한글).md      ← 읽는 방법 안내
│   ├── [설계 문서] CardFit (한글).md
│   ├── [테스트 명세서] CardFit (한글).md
│   ├── [배포 게이트 데이터] CardFit (한글).md
│   ├── [태스크 리스트] CardFit.md
│   ├── [GitHub 프로젝트용 TASK 템플릿] CardFit.md
│   ├── [태스크 추출 방법론 적합성 평가] CardFit.md
│   ├── [태스크 축약 분석] CardFit.md
│   └── tasks/                                ← 배치별 이슈 명세
│       └── S1-계약-API.md                     (CT-01 · CT-02)
├── .github/ISSUE_TEMPLATE/
│   └── feature-task.md                       ← GitHub 이슈 템플릿
└── tools/                                    ← 실행 도구
    ├── verify_docs.py                        ← 문서 정합성 검증
    ├── build_task_graph.py                   ← Blocks 생성·위상 정렬
    ├── apply_task_merge.py                   ← 병합 맵 적용·표 생성
    ├── task_merge_map.json                   ← 병합 맵 (142→53)
    ├── generate_boundary_cases.py            ← 경계값 케이스 생성
    ├── scan_prohibited_terms.py              ← 금지어 스캐너
    ├── boundary-cases.json                   ← 생성물 (260건)
    ├── prohibited-terms.json                 ← 금지어 사전
    └── scan-samples.json                     ← 스캐너 회귀 샘플
```

> **표준 원문 PDF는 저장소에 포함하지 않습니다.** ISO/IEC/IEEE 29148:2018은 유료 저작물이라 `.gitignore`로 제외했습니다. 작업 시 프로젝트 루트에 두고 참조하세요.

---

## 3. 산출물

| 문서 ID | 파일 | 내용 |
| --- | --- | --- |
| **PRD-CARDFIT-001** | `cardfit-prd-v1_0.md` | 입력 PRD 겸 요구사항 추적표 |
| **SRS-CARDFIT-001** | `docs/[SRS 문서] CardFit (한글).md` | 요구사항 27건 · 다이어그램 17개 |
| **GUIDE-CARDFIT-001** | `docs/[SRS 이해 가이드] CardFit (한글).md` | SRS를 읽는 방법 — 경로 3종 · 자가진단 12문항 |
| **SDD-CARDFIT-001** | `docs/[설계 문서] CardFit (한글).md` | 다이어그램 27개 · 클래스·시퀀스·순서도·상태 |
| **STD-CARDFIT-001** | `docs/[테스트 명세서] CardFit (한글).md` | 테스트 27건 (P0 6건 · 배포 게이트 2건) |
| **GTD-CARDFIT-001** | `docs/[배포 게이트 데이터] CardFit (한글).md` | 경계값 260건 · 금지어 사전 |
| **TASK-CARDFIT-001** | `docs/[태스크 리스트] CardFit.md` | 개발 98건 + 디자인 9건 |

### 3.1 문서 파생 관계

```
PRD ──> SRS ──┬──> SDD  (어떻게 만드나)
              ├──> STD  (어떻게 확인하나) ──> GTD (게이트 입력)
              └──> TASK (무엇부터 하나)
```

---

## 4. SRS 구성

| 장 | 출처 | 근거 조항 |
| :---: | --- | --- |
| 1~7 | 예시 SRS 양식 | — |
| **8** 사용자 특성 | PRD 2절 | 9.6.6 User characteristics |
| **9** 설계 결정 기록 (ADR) | PRD 10-1 | 9.6.16 · 9.6.20 |
| **10** 가정 및 의존성 | PRD 10-2~4 | 9.6.8 · 9.6.7 |
| **11** 검증 | PRD 7·8절 | 9.6.19 Verification |
| **12** 재설정 규칙 | PRD 11절 | 9.6.20 |

절 단위 확장 — **1.5**(9.6.7 기술 제약) · **4.1 배분**(9.6.9) · **4.3**(9.6.12 c) · **6.5**(9.6.12 b) · **6.6**(9.6.15)

---

## 5. 도구

```bash
# 문서 정합성 검증 — 20개 항목
python3 tools/verify_docs.py

# 경계값 케이스 생성 (배포 게이트 ①)
python3 tools/generate_boundary_cases.py
python3 tools/generate_boundary_cases.py --abs 30000 --rel 0.10 --delta 0.20   # D2·D5 확정 후

# 금지어 스캔 (배포 게이트 ②)
python3 tools/scan_prohibited_terms.py --dict tools/prohibited-terms.json --samples tools/scan-samples.json
```

`verify_docs.py`는 **문서에 적힌 수와 실제로 세어본 수가 다르면 실패**로 봅니다. 요구사항 27건이 세 추적표에 모두 있는지, ERD 엔터티와 DDL 테이블이 일치하는지, 게이트 데이터 개수 표기가 맞는지 등을 검사합니다.

---

## 6. 현재 상태

| 단계 | 상태 |
| --- | --- |
| PRD 최종 검토·수정 | ✅ 미확인 가설 경고 제거, 기준선·의존성·비용 NFR·ADR 보강 |
| SRS 변환 (1~7장) + 확장 (8~12장) | ✅ 요구사항 27건 · 다이어그램 17개 |
| 설계 문서 (SDD) | ✅ UseCase·Component·Class·Sequence·Flowchart·State |
| 테스트 명세서 (STD) | ✅ 27건 · 추적표 전건 일치 |
| 배포 게이트 데이터 (GTD) | ✅ D8 해소 — 경계값 260건 · 스캐너 검증 통과 |
| 태스크 리스트 (TASK) | ✅ **v2.0 축약판 53건** · 커버리지 142/142 · 차단 7건 |
| Phase 0 방법론 적합화 | ✅ CT·MK 신설 · CQRS 분해 · TS 27건 · Blocks 자동 생성 |
| **Phase 1 — 배치 1 이슈 명세** | ✅ **CT-01 · CT-02** (`docs/tasks/S1-계약-API.md`) |
| **D16 규칙 엔진 계산 명세** | 🔴 **미정 — 기획 결정 필요** (SRS 4.1.0 RE-1~RE-8) |
| D2 · D5 · D11 · D4 · DEC-3b | 🔴 미정 |

### 6.1 다음 결정

**D16(규칙 엔진 계산 명세)이 최우선입니다.** 태스크 5건을 동시에 막고 있고, D2(임계값)보다 선행해야 합니다 — 전환비용 산정 기준(RE-5) 없이 임계값을 정하면 임계값이 무의미해집니다.

---

## 7. 원칙

1. **포맷은 예시 SRS를 따른다.** 표준 원문은 확장이 필요한 부분에서만 참조한다.
2. **확장은 최소 범위로 한다.** 표준을 채우기 위한 빈 절은 만들지 않는다.
3. **없는 내용을 만들지 않는다.** 미정 사항은 `TBD`로 남기고 무엇이 막혀 있는지 함께 적는다.
4. **PRD의 판단을 보존한다.** Net Benefit 게이팅, 스코프 경계, Guardrail 0건 기준은 설계 의도이므로 변환 과정에서 희석하지 않는다.
5. **개수를 주장하지 않고 센다.** 문서에 적은 수치는 `tools/verify_docs.py`가 실측과 대조한다.
