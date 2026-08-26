---
name: 101-build-and-env-setup
description: 로컬 개발환경 기동 절차 — Supabase·Prisma·픽스처 시드. 처음 클론했거나 환경이 깨졌을 때 사용한다.
---
# 개발환경 기동

## 1. 전제

| 도구 | 용도 |
| --- | --- |
| Node.js LTS | Next.js |
| Supabase CLI | 로컬 PostgreSQL |
| Python 3 | 문서 검증·픽스처 생성 도구 |
| `gh` | 이슈·프로젝트 관리 |

## 2. 환경변수

`.env.example` 을 `.env.local` 로 복사하고 채운다.

| 변수 | 값 |
| --- | --- |
| `DATABASE_URL` | 로컬 Supabase 연결 문자열 |
| `CARDFIT_DATA_MODE` | **`fixture`** (기본) |
| AI 모델 식별자 | Gemini. fixture 모드에서는 호출되지 않는다 |

**변수가 없으면 명시적 오류로 실패해야 한다.** 조용히 기본값으로 뜨면 어떤 모드로 도는지 알 수 없다.

## 3. 기동

```bash
supabase start                      # 로컬 DB
npx prisma migrate dev              # 스키마 적용
npm run seed:fixtures               # 픽스처 적재 (DA-05 → DA-06 순서)
npm run dev                         # 개발 서버
```

## 4. 확인

```bash
python3 tools/verify_docs.py        # 문서 110항목
python3 tools/generate_fixtures.py  # 픽스처 재생성·대조
npm run verify                      # 타입·린트·테스트 (IN-01이 만든다)
```

## 5. 자주 막히는 곳

| 증상 | 원인 |
| --- | --- |
| 기동 즉시 종료 | `CARDFIT_DATA_MODE` 미설정 |
| 마이그레이션 실패 | Supabase 미기동 · `DATABASE_URL` 불일치 |
| 픽스처 적재 순서 오류 | `DA-05`(상품)가 `DA-06`(페르소나)보다 먼저여야 한다 |
| 외부 호출 발생 | 모드가 `live` 로 설정됨 |

## 참고
Vercel 배포는 `.claude/skills/deploy-to-vercel/`, Prisma 초기화는 `.claude/skills/prisma-database-setup/` 을 본다.
