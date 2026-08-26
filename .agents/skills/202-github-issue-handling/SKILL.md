---
name: 202-github-issue-handling
description: GitHub 이슈·프로젝트 동기화 절차. 태스크 상태를 옮기거나, 이슈 본문을 고치거나, 일정을 다시 계산해 프로젝트에 반영할 때 사용한다.
---

# 이슈·프로젝트 운영

## 대응 관계

**태스크 1건 = 파일 1개 = 이슈 1건.** 매핑은 `tools/issue-map.json` 이 정본이다.

| 위치 | 무엇 |
| --- | --- |
| `docs/tasks/<ID>.md` | 명세 원본 — **여기를 먼저 고친다** |
| GitHub 이슈 `#1~#59` | 위 파일의 사본 + 원본 링크 |
| 프로젝트 #1 | 상태 · 일정 필드 (Start/Target date · Track · Week · Duration · Slack) |

## 이슈 본문을 고칠 때

**파일을 먼저 고치고 이슈에 반영한다.** 반대로 하면 원본이 낡는다.

```bash
gh issue edit <번호> --repo maybeaj/cardfit-prd-to-srs --body-file <파일>
```

본문 머리에는 원본 명세 링크와 태스크 리스트 링크를 붙인다.

## 상태 전이

| 상태 | 조건 |
| --- | --- |
| Todo | 선행이 전건 Done |
| In Progress | 착수 조건(DoR) 충족 후 |
| Done | **공통 DoD 8항목 전건 통과** |

**선행이 안 끝난 태스크를 In Progress 로 옮기지 않는다.** 의존 관계는 추정이 아니라 문서에 확정돼 있다.

## 일정을 다시 계산할 때

의존 관계나 소요가 바뀌면 프로젝트 필드를 다시 채운다.

```bash
python3 tools/setup_github_project.py --dry-run   # 산정만 확인
python3 tools/setup_github_project.py             # 필드 주입 (재개 안전)
```

**⚠️ SINGLE_SELECT 옵션을 나중에 재정의하면 이미 설정된 값이 전부 초기화된다.** 옵션 범위는 처음부터 넉넉히 잡는다.

## 태스크가 늘거나 줄 때

1. `tools/task_merge_map.json` 수정
2. `python3 tools/apply_task_merge.py --emit` 으로 표 재생성 → 태스크 리스트 반영
3. `docs/tasks/<ID>.md` 신설·수정
4. 이슈 발급 후 `tools/issue-map.json` 갱신
5. 실행 총괄의 Gantt·대조표 재생성
6. `python3 tools/verify_docs.py` — **Gantt ID 집합과 태스크 ID 집합이 어긋나면 여기서 걸린다**

## 로드맵 뷰

날짜 필드 바인딩은 **API가 노출하지 않는다.** UI에서 지정한다 — Layout: Roadmap · Date fields: Start date / Target date.
