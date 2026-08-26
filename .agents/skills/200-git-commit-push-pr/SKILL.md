---
name: 200-git-commit-push-pr
description: 저장소 관례에 맞춘 커밋·PR 작성. 커밋 단위를 나누거나 PR을 열 때 사용한다.
---
# 커밋·PR

대상: **$ARGUMENTS**

## 1. 상태 확인

```bash
git status --short --branch
git log --oneline -5          # 이 저장소의 메시지 관례를 먼저 본다
```

**기본 브랜치에 직접 커밋하지 않는다.** 브랜치를 따고 작업한 뒤 병합한다.

## 2. 커밋 전 검증

```bash
python3 tools/verify_docs.py
python3 tools/generate_fixtures.py    # 픽스처·계산이 바뀌었으면
```

**통과하지 못한 상태로 커밋하지 않는다.**

## 3. 단위 나누기

원자적으로 나눈다 — 한 커밋이 한 가지를 한다. 문서와 코드가 함께 바뀌었으면 같은 커밋에 둔다(문서가 코드의 근거이므로 갈라지면 안 된다).

## 4. 메시지 형식

이 저장소의 관례를 따른다.

```
type: 제목 — 부제

한두 문장으로 왜 이 변경이 필요했는지.

① 첫 번째 묶음

- 구체적 변경
- 판단이 들어간 곳은 이유를 함께

② 두 번째 묶음

...

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
```

| type | 쓰임 |
| --- | --- |
| `feat` | 새 기능·산출물 |
| `fix` | 결함 수정 |
| `refactor` | 구조 변경 (동작 동일) |
| `docs` | 문서 |
| `chore` | 도구·설정 |

**숫자를 적을 때는 실측값을 쓴다.** "약 50건" 대신 세어본 수를 적는다.

## 5. 이슈 연결

태스크 작업이면 본문에 이슈를 참조한다. 태스크 ID ↔ 이슈 번호는 `tools/issue-map.json` 에 있다.

## 6. PR

```bash
gh pr create --title "..." --body "..."
```

본문 끝에 붙인다.

```
🤖 Generated with [Claude Code](https://claude.com/claude-code)
```

**커밋·푸시는 사용자가 요청했을 때만 한다.**
