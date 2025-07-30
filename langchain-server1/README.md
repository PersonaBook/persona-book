# 🚀 상태 머신 기반 Java Learning Chat System

ChatState enum을 사용한 상태 관리와 FastAPI 호출을 통한 기능 처리를 구현한 시스템입니다.

## 📁 파일 구조

```
last_ai/
├── core/
│   ├── state_machine.py          # 상태 머신 및 FastAPI 클라이언트
│   ├── models.py                 # AI 모델 관리
│   ├── vector_store.py           # 벡터 스토어 관리
│   ├── chains.py                 # LangChain 체인 관리
│   └── concept_explainer.py      # 개념 설명 시스템
├── generators/
│   └── question_generator.py     # 문제 생성기
├── analyzers/
│   └── adaptive_learning.py      # 적응형 학습 분석기
├── utils/
│   └── file_manager.py           # 파일 관리
├── main.py                       # 메인 실행 파일
├── config.json                   # 설정 파일
├── requirements.txt               # 의존성 목록
└── README.md                     # 이 파일
```

## 🔧 설치 및 실행

### 1. 의존성 설치

```bash
pip install -r requirements.txt
```

### 2. 환경 변수 설정

`.env` 파일을 생성하고 OpenAI API 키를 설정하세요:

```bash
OPENAI_API_KEY=your_openai_api_key_here
```

또는 `config.json`에 직접 설정:

```json
{
  "openai_api_key": "your_openai_api_key_here"
}
```

### 3. PDF 파일 설정

Java 교재 PDF 파일의 경로를 설정하세요:

```bash
export JAVA_PDF_PATH=/path/to/your/java_textbook.pdf
```

또는 `config.json`에 설정:

```json
{
  "pdf_path": "/path/to/your/java_textbook.pdf"
}
```

### 4. 시스템 실행

```bash
python main.py
```

## 🎯 주요 기능

### 1. 예상문제 생성
- 챕터/페이지 선택 기반 문제 생성
- 특정 개념 선택 기반 문제 생성
- RAG 기반 컨텍스트 활용

### 2. 학습보충 (개념 설명)
- 오답 시 자동 개념 설명 제공
- 사용자 평가 기반 설명 개선
- 피드백 기반 재설명

### 3. 페이지 찾기
- 키워드 기반 페이지 검색
- 챕터별 분류된 결과 제공

## 🔄 상태 전이 흐름

```
START
  ↓
WAITING_USER_SELECT_FEATURE
  ├─ 1. 예상 문제 생성 선택
  │     ↓
  │   WAITING_PROBLEM_CRITERIA_SELECTION
  │     ↓
  │   WAITING_PROBLEM_CONTEXT_INPUT
  │     ↓
  │   GENERATING_QUESTION_WITH_RAG (FastAPI 호출)
  │     ↓
  │   QUESTION_PRESENTED_TO_USER
  │     ↓
  │   WAITING_USER_ANSWER
  │     ↓
  │   EVALUATING_ANSWER_AND_LOGGING (FastAPI 호출)
  │     ├─ 정답 → WAITING_NEXT_ACTION_AFTER_LEARNING
  │     └─ 오답 → PRESENTING_CONCEPT_EXPLANATION
  │
  ├─ 2. 학습보충 선택
  │     ↓
  │   WAITING_CONCEPT_INPUT
  │     ↓
  │   PRESENTING_CONCEPT_EXPLANATION
  │
  └─ 3. 페이지 찾기 선택
        ↓
    WAITING_KEYWORD_FOR_PAGE_SEARCH
        ↓
    PROCESSING_PAGE_SEARCH_RESULT (FastAPI 호출)
```

## 💻 사용 예시

### 문제 생성 및 풀이

```
🎯 **Java 학습 시스템**
============================================================
1️⃣  예상문제 생성
2️⃣  학습보충 (개념 설명)
3️⃣  페이지 찾기
0️⃣  종료
============================================================

선택하세요: 1

🤖 시스템: 문제 생성을 선택하셨습니다. 어떤 방식으로 문제를 생성하시겠습니까?
1. 챕터/페이지 선택
2. 특정 개념 선택

선택하세요: 1

🤖 시스템: 챕터/페이지 선택을 선택하셨습니다. 챕터명 또는 페이지 범위를 입력해주세요.
예시: Chapter1 - 변수, 30-50페이지

입력해주세요: Chapter1 - 변수

🔍 FastAPI 호출 시뮬레이션: RAG 기반 문제 생성
   - Context: Chapter1 - 변수

🤖 시스템: 문제가 생성되었습니다 (품질: 0.8):
Java에서 변수의 선언과 초기화에 대한 설명으로 옳은 것은?
1. 변수는 선언과 동시에 반드시 초기화해야 한다.
2. 변수는 선언 후 나중에 초기화할 수 있다.
3. 변수는 한 번 초기화하면 값을 변경할 수 없다.
4. 변수는 메서드 내에서만 선언할 수 있다.
정답을 선택해주세요 (1-4):

입력해주세요: 2

🎉 정답입니다!

다음 중 선택해주세요:
1. 다음 문제 풀기
2. 다른 기능으로 돌아가기
```

## 🛠️ 개발 정보

### 주요 클래스

- **JavaLearningSystem**: 메인 시스템 클래스
- **StateMachine**: 상태 관리 및 전이
- **FastAPIClient**: FastAPI 서버와의 통신
- **QuestionGenerator**: RAG 기반 문제 생성
- **ConceptExplainer**: 개념 설명 생성

### FastAPI 호출 대상 상태

| 상태 | 설명 | 기능 |
|------|------|------|
| `GENERATING_QUESTION_WITH_RAG` | RAG 기반 문제 생성 | 문제 생성 |
| `EVALUATING_ANSWER_AND_LOGGING` | 답변 평가 및 로깅 | 답변 평가 |
| `PRESENTING_CONCEPT_EXPLANATION` | 개념 설명 생성 | 개념 설명 |
| `REEXPLAINING_CONCEPT` | 개념 재설명 | 재설명 |
| `PROCESSING_PAGE_SEARCH_RESULT` | 페이지 검색 | 검색 |

## 🚨 주의사항

1. **OpenAI API 키 필수**: 시스템 실행 전 API 키 설정이 필요합니다.
2. **PDF 파일 경로**: Java 교재 PDF 파일의 경로를 올바르게 설정해야 합니다.
3. **인터넷 연결**: OpenAI API 호출을 위해 인터넷 연결이 필요합니다.

## 🔄 업데이트

### 새로운 상태 추가
1. `ChatState` enum에 새 상태 추가
2. `JavaLearningSystem`에 해당 상태 처리 메서드 추가
3. FastAPI 엔드포인트 추가 (필요시)

### 새로운 기능 추가
1. 새로운 핸들러 메서드 추가
2. 상태 전이 로직 수정
3. 사용자 인터페이스 업데이트

---

**만든이**: KimDaehwa  
**버전**: 1.0.0  
**최종 업데이트**: 2024-01-01 