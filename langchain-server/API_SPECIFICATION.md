# Langchain-Server API 명세서

## 개요
Langchain-Server는 Java 학습을 위한 RAG 기반 연습문제 생성 및 채팅 서비스를 제공하는 FastAPI 애플리케이션입니다.

## 기본 정보
- **Base URL**: `http://localhost:8000`
- **API 버전**: v1
- **문서**: `http://localhost:8000/docs` (Swagger UI)
- **OpenAPI JSON**: `http://localhost:8000/openapi.json`

## 인증
현재 API는 인증 없이 사용 가능합니다.

---

## 1. 헬스 체크 API

### 1.1 서버 상태 확인
```http
GET /api/v1/ping
```

**응답 예시:**
```json
{
  "status": "ok"
}
```

---

## 2. 연습문제 생성 API

### 2.1 연습문제 생성
```http
POST /api/v1/generate-question
```

**요청 본문:**
```json
{
  "pdf_base64": "Base64로 인코딩된 PDF 문자열",
  "query": "Java 변수와 데이터 타입",
  "difficulty": "보통",
  "question_type": "객관식",
  "max_pages": 10,
  "count": 1
}
```

**요청 파라미터:**
| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| pdf_path | string | ✅ | PDF 파일 경로 |
| query | string | ✅ | 검색 쿼리 (문제 생성 주제) |
| difficulty | string | ❌ | 난이도 (기본값: "보통") |
| question_type | string | ❌ | 문제 유형 (기본값: "객관식") |
| max_pages | integer | ❌ | 처리할 최대 페이지 수 |
| count | integer | ❌ | 생성할 문제 수 (기본값: 1) |

**응답 예시:**
```json
{
  "success": true,
  "message": "연습문제 생성이 완료되었습니다.",
  "questions": [
    "문제: 다음 중 Java에서 변수의 초기화에 대한 설명으로 옳지 않은 것은 무엇입니까?\n\nA) 변수는 선언과 동시에 초기화할 수 있다.\nB) 초기화하지 않은 지역 변수는 사용하기 전에 반드시 초기화를 해야 한다.\nC) 인스턴스 변수는 자동으로 기본값으로 초기화된다.\nD) 클래스 변수는 초기화하지 않으면 컴파일 오류가 발생한다.\n\n정답: D\n\n해설: Java에서 클래스 변수는 자동으로 기본값으로 초기화됩니다."
  ],
  "chunks_count": 35
}
```

### 2.2 PDF 처리 테스트
```http
POST /api/v1/test-pdf-processing
```

**쿼리 파라미터:**
| 파라미터 | 타입 | 필수 | 설명 |
|----------|------|------|------|
| pdf_path | string | ✅ | PDF 파일 경로 |
| max_pages | integer | ❌ | 처리할 최대 페이지 수 (기본값: 5) |

**응답 예시:**
```json
{
  "success": true,
  "message": "PDF 처리 테스트 완료",
  "chunks_count": 16,
  "sample_chunk": "Java의 기본 자료형에는 int, char, boolean, byte, short, long, float, double의 8가지가 있습니다..."
}
```

---

## 3. 채팅 API

### 3.1 채팅 메시지 처리
```http
POST /api/v1/chat
```

**요청 본문:**
```json
{
  "userId": "user123",
  "bookId": "book456",
  "content": "Java 변수와 데이터 타입",
  "chatState": "GENERATING_QUESTION_WITH_RAG"
}
```

**요청 파라미터:**
| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| userId | string | ✅ | 사용자 ID |
| bookId | string | ✅ | 책 ID |
| content | string | ✅ | 메시지 내용 |
| chatState | string | ✅ | 채팅 상태 |

**ChatState 값:**
- `WAITING_USER_SELECT_FEATURE`: 기능 선택 대기
- `WAITING_PROBLEM_CRITERIA_SELECTION`: 문제 기준 선택 대기
- `WAITING_PROBLEM_CONTEXT_INPUT`: 문제 컨텍스트 입력 대기
- `GENERATING_QUESTION_WITH_RAG`: RAG 기반 문제 생성
- `GENERATING_ADDITIONAL_QUESTION_WITH_RAG`: 추가 문제 생성
- `EVALUATING_ANSWER_AND_LOGGING`: 정답 평가 및 로깅
- `WAITING_NEXT_ACTION_AFTER_LEARNING`: 학습 후 다음 행동 대기
- `PRESENTING_CONCEPT_EXPLANATION`: 개념 설명 제공
- `WAITING_CONCEPT_RATING`: 개념 평가 대기
- `WAITING_REASON_FOR_LOW_RATING`: 낮은 평가 이유 대기
- `REEXPLAINING_CONCEPT`: 개념 재설명
- `WAITING_CONCEPT_INPUT`: 개념 입력 대기
- `WAITING_KEYWORD_FOR_PAGE_SEARCH`: 페이지 검색 키워드 대기
- `PROCESSING_PAGE_SEARCH_RESULT`: 페이지 검색 결과 처리

**응답 예시:**
```json
{
  "userId": "user123",
  "bookId": "book456",
  "content": "문제: 다음 중 Java에서 변수의 초기화에 대한 설명으로 옳지 않은 것은 무엇입니까?\n\nA) 변수는 선언과 동시에 초기화할 수 있다.\nB) 초기화하지 않은 지역 변수는 사용하기 전에 반드시 초기화를 해야 한다.\nC) 인스턴스 변수는 자동으로 기본값으로 초기화된다.\nD) 클래스 변수는 초기화하지 않으면 컴파일 오류가 발생한다.\n\n정답: D\n\n해설: Java에서 클래스 변수는 자동으로 기본값으로 초기화됩니다.",
  "messageType": "TEXT",
  "sender": "AI",
  "chatState": "GENERATING_QUESTION_WITH_RAG"
}
```

---

## 4. 채팅 기록 API

### 4.1 채팅 기록 저장
```http
POST /api/v1/chat-history
```

**요청 본문:**
```json
{
  "userId": "user123",
  "bookId": "book456",
  "content": "사용자 메시지",
  "messageType": "TEXT",
  "sender": "USER",
  "chatState": "GENERATING_QUESTION_WITH_RAG"
}
```

### 4.2 채팅 기록 조회
```http
GET /api/v1/chat-history/{user_id}
```

**응답 예시:**
```json
[
  {
    "id": "chat_123",
    "userId": "user123",
    "bookId": "book456",
    "content": "Java 변수와 데이터 타입",
    "messageType": "TEXT",
    "sender": "USER",
    "chatState": "GENERATING_QUESTION_WITH_RAG",
    "timestamp": "2024-01-15T10:30:00Z"
  }
]
```

---

## 5. OpenAI 채팅 API

### 5.1 OpenAI 직접 채팅
```http
POST /api/v1/openai-chat
```

**요청 본문:**
```json
{
  "messages": [
    {
      "role": "user",
      "content": "Java 변수에 대해 설명해주세요."
    }
  ],
  "model": "gpt-4o",
  "temperature": 0.7,
  "max_tokens": 2000
}
```

**응답 예시:**
```json
{
  "response": "Java에서 변수는 데이터를 저장하는 메모리 공간입니다...",
  "usage": {
    "prompt_tokens": 15,
    "completion_tokens": 150,
    "total_tokens": 165
  }
}
```

---

## 6. 에러 응답

### 6.1 일반 에러
```json
{
  "detail": "에러 메시지"
}
```

### 6.2 검증 에러
```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["body", "field_name"],
      "msg": "Field required",
      "input": null
    }
  ]
}
```

---

## 7. 사용 예시

### 7.1 연습문제 생성
```bash
curl -X POST "http://localhost:8000/api/v1/generate-question" \
  -H "Content-Type: application/json" \
  -d '{
    "pdf_path": "./javajungsuk4_sample.pdf",
    "query": "Java 배열과 반복문",
    "difficulty": "보통",
    "question_type": "객관식",
    "max_pages": 10,
    "count": 3
  }'
```

### 7.2 채팅 메시지
```bash
curl -X POST "http://localhost:8000/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "user123",
    "bookId": "book456",
    "content": "Java 변수와 데이터 타입",
    "chatState": "GENERATING_QUESTION_WITH_RAG"
  }'
```

---

## 8. 환경 설정

### 8.1 필수 환경 변수
```bash
OPENAI_API_KEY=your_openai_api_key
ELASTICSEARCH_HOSTS=http://localhost:9200
```

### 8.2 선택적 환경 변수
```bash
LANGCHAIN_TRACING=true
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
LANGSMITH_API_KEY=your_langsmith_api_key
```

---

## 9. 성능 최적화

### 9.1 캐싱
- PDF 처리 결과는 자동으로 캐시됩니다
- 두 번째 요청부터는 캐시된 청크를 사용하여 속도가 크게 향상됩니다

### 9.2 권장 설정
- `max_pages`: 5-10 (테스트용), 50-100 (실제 사용)
- `count`: 1-3 (단일 요청당)
- `difficulty`: "쉬움", "보통", "어려움"

---

## 10. 제한사항

- PDF 파일은 현재 `javajungsuk4_sample.pdf`만 지원
- Elasticsearch가 실행 중이어야 함
- OpenAI API 키가 필요
- 대용량 PDF 처리 시 시간이 오래 걸릴 수 있음

---

## 11. 개발 정보

- **프레임워크**: FastAPI
- **Python 버전**: 3.12+
- **주요 라이브러리**: Langchain, OpenAI, PyMuPDF, Elasticsearch
- **문서**: `http://localhost:8000/docs`
- **리포지토리**: [GitHub 링크] 