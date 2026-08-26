---
description: 문서·픽스처·게이트 전체 검증을 한 번에 수행한다
allowed-tools: Bash, Read
---

# 전체 검증

아래를 순서대로 실행하고 **실패한 항목만** 원인과 함께 보고한다. 전부 통과하면 한 줄로 요약한다.

## 1. 문서 정합성 (110항목)

```bash
python3 tools/verify_docs.py
```

주장(문서에 적힌 수)과 실측(실제로 세어본 수)이 다르면 실패다. 요구사항 27건이 세 추적표에 모두 있는지, ERD와 DDL이 일치하는지, 태스크 파일 규칙과 Gantt ID 집합이 맞는지 등을 본다.

## 2. 픽스처 + 참조 계산기

```bash
python3 tools/generate_fixtures.py
```

페르소나 5인의 결론이 의도한 값과 일치하는지 대조한다. **어긋나면 생성이 실패한다.**

## 3. 배포 게이트 ② — 금지어

```bash
python3 tools/scan_prohibited_terms.py --dict tools/prohibited-terms.json --samples tools/scan-samples.json
```

## 4. 태스크 그래프

```bash
python3 tools/build_task_graph.py
python3 tools/apply_task_merge.py
```

순환 0 · 선행 참조 무결성을 확인한다.

## 5. 코드가 있으면

```bash
npm run verify     # 타입 검사 + 린트 + 테스트 (IN-01이 만든다)
```

의존성 경계 린트(`IN-04`)가 여기 포함된다 — **AI가 계산 클래스를 참조하면 여기서 걸린다.**

## 보고 형식

```
✅ 문서 110항목 · 픽스처 5인 · 금지어 53건 · 그래프 59노드
❌ (있으면) 어느 검사가 왜 실패했는지 + 재현 명령
```
