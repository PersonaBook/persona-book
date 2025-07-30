# RAG API Documentation

## 개요

이 문서는 RAG(Retrieval-Augmented Generation) 기반 학습 지원 API들의 사용법을 설명합니다.

## API 목록

### 1. GENERATING_QUESTION_WITH_RAG
**엔드포인트:** `POST /api/v1/generate-question-with-rag`

RAG를 사용하여 PDF 기반 문제를 생성합니다.

**요청 예시:**
```json
{
  "userId": 123,
  "bookId": 456,
  "pdf_base64": "base64_encoded_pdf_data",
  "query": "Java 변수와 데이터 타입에 대한 문제를 만들어주세요",
  "difficulty": "보통",
  "question_type": "객관식",
  "max_pages": 5
}
```

**응답 예시:**
```json
{
  "success": true,
  "message": "RAG를 사용한 문제 생성이 완료되었습니다.",
  "userId": 123,
  "bookId": 456,
  "question": "다음 중 Java에서 변수의 초기화에 대한 설명으로 옳지 않은 것은?",
  "correct_answer": "D",
  "explanation": "Java에서 클래스 변수는 자동으로 기본값으로 초기화됩니다.",
  "difficulty": "보통",
  "question_type": "객관식",
  "chunks_used": 5,
  "processing_time": 2.34,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### 2. GENERATING_ADDITIONAL_QUESTION_WITH_RAG
**엔드포인트:** `POST /api/v1/generate-additional-question-with-rag`

RAG를 사용하여 추가 문제를 생성합니다.

**요청 예시:**
```json
{
  "userId": 123,
  "bookId": 456,
  "pdf_base64": "base64_encoded_pdf_data",
  "query": "추가 문제를 만들어주세요",
  "previous_question_type": "객관식",
  "difficulty": "보통",
  "max_pages": 5
}
```

**응답 예시:**
```json
{
  "success": true,
  "message": "RAG를 사용한 추가 문제 생성이 완료되었습니다.",
  "userId": 123,
  "bookId": 456,
  "additional_question": "Java에서 배열의 선언과 초기화 방법을 설명하세요.",
  "correct_answer": "int[] numbers = {1, 2, 3, 4, 5};",
  "explanation": "배열은 데이터 타입과 함께 선언하고 중괄호로 초기화할 수 있습니다.",
  "difficulty": "보통",
  "question_type": "주관식",
  "chunks_used": 5,
  "processing_time": 2.15,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### 3. EVALUATING_ANSWER_AND_LOGGING
**엔드포인트:** `POST /api/v1/evaluate-answer-and-log`

사용자 답안을 평가하고 로깅합니다.

**요청 예시:**
```json
{
  "userId": 123,
  "bookId": 456,
  "question": "Java에서 변수의 선언 방법은?",
  "user_answer": "int number = 10;",
  "correct_answer": "int number = 10;",
  "explanation": "변수는 데이터 타입과 함께 선언하고 초기화할 수 있습니다.",
  "evaluation": "정답"
}
```

**응답 예시:**
```json
{
  "success": true,
  "message": "답안 평가가 완료되었습니다.",
  "userId": 123,
  "bookId": 456,
  "is_correct": true,
  "evaluation_message": "✅ 정답입니다! 잘 하셨네요.",
  "detailed_feedback": "정답입니다! 변수 선언을 잘 이해하고 계시네요.",
  "score": 100.0,
  "learning_suggestions": [
    "이 개념을 다른 문제에도 적용해보세요.",
    "관련된 고급 개념도 학습해보세요."
  ],
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### 4. PRESENTING_CONCEPT_EXPLANATION
**엔드포인트:** `POST /api/v1/present-concept-explanation`

RAG를 사용하여 개념을 설명합니다.

**요청 예시:**
```json
{
  "userId": 123,
  "bookId": 456,
  "pdf_base64": "base64_encoded_pdf_data",
  "concept_query": "Java 클래스와 객체에 대해 설명해주세요",
  "user_level": "초급",
  "max_pages": 5
}
```

**응답 예시:**
```json
{
  "success": true,
  "message": "개념 설명이 완료되었습니다.",
  "userId": 123,
  "bookId": 456,
  "concept_name": "Java 클래스와 객체",
  "explanation": "클래스는 객체를 생성하기 위한 템플릿입니다...",
  "examples": [
    "public class Student { private String name; }",
    "Student student = new Student();"
  ],
  "key_points": [
    "클래스는 객체의 설계도",
    "객체는 클래스의 인스턴스",
    "캡슐화, 상속, 다형성 지원"
  ],
  "related_concepts": [
    "인스턴스 변수",
    "메서드",
    "생성자"
  ],
  "difficulty_level": "초급",
  "chunks_used": 7,
  "processing_time": 3.45,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### 5. REEXPLAINING_CONCEPT
**엔드포인트:** `POST /api/v1/reexplain-concept`

RAG를 사용하여 개념을 재설명합니다.

**요청 예시:**
```json
{
  "userId": 123,
  "bookId": 456,
  "pdf_base64": "base64_encoded_pdf_data",
  "original_concept": "Java 클래스와 객체",
  "user_feedback": "이해가 안 됩니다. 더 쉽게 설명해주세요",
  "difficulty_level": "더 쉬운",
  "max_pages": 5
}
```

**응답 예시:**
```json
{
  "success": true,
  "message": "개념 재설명이 완료되었습니다.",
  "userId": 123,
  "bookId": 456,
  "concept_name": "Java 클래스와 객체",
  "reexplanation": "클래스를 집을 짓는 설계도라고 생각해보세요...",
  "simplified_explanation": "클래스 = 설계도, 객체 = 실제 집",
  "visual_aids": [
    "클래스 다이어그램",
    "객체 관계도"
  ],
  "step_by_step_guide": [
    "1. 클래스 정의하기",
    "2. 객체 생성하기",
    "3. 메서드 호출하기"
  ],
  "common_misconceptions": [
    "클래스와 객체를 혼동하는 경우",
    "인스턴스 변수와 지역 변수 구분 못하는 경우"
  ],
  "difficulty_level": "더 쉬운",
  "chunks_used": 7,
  "processing_time": 3.67,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### 6. PROCESSING_PAGE_SEARCH_RESULT
**엔드포인트:** `POST /api/v1/process-page-search-result`

RAG를 사용하여 페이지 검색 결과를 처리합니다.

**요청 예시:**
```json
{
  "userId": 123,
  "bookId": 456,
  "pdf_base64": "base64_encoded_pdf_data",
  "search_keyword": "Java 배열",
  "search_type": "concept",
  "max_results": 5,
  "max_pages": 5
}
```

**응답 예시:**
```json
{
  "success": true,
  "message": "'Java 배열'에 대한 검색이 완료되었습니다.",
  "userId": 123,
  "bookId": 456,
  "search_keyword": "Java 배열",
  "search_results": [
    {
      "id": 1,
      "content": "Java에서 배열은 동일한 타입의 데이터를 순차적으로 저장하는 자료구조입니다...",
      "page_number": 15,
      "result_type": "concept_definition",
      "relevance_score": 0.9,
      "word_count": 150
    }
  ],
  "total_results": 5,
  "relevant_pages": [15, 16, 17],
  "summary": "Java 배열에 대한 개념과 사용법이 15-17페이지에 상세히 설명되어 있습니다...",
  "search_type": "concept",
  "chunks_used": 5,
  "processing_time": 1.23,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## 공통 필드 설명

### 요청 공통 필드
- `userId`: 사용자 ID (int)
- `bookId`: 책 ID (int)
- `pdf_base64`: Base64로 인코딩된 PDF 데이터 (string)
- `max_pages`: 처리할 최대 페이지 수 (optional, int)

### 응답 공통 필드
- `success`: 성공 여부 (boolean)
- `message`: 응답 메시지 (string)
- `userId`: 사용자 ID (int)
- `bookId`: 책 ID (int)
- `chunks_used`: 사용된 청크 수 (int)
- `processing_time`: 처리 시간 (float, 초 단위)
- `timestamp`: 생성 시간 (datetime)

## 에러 처리

모든 API는 다음과 같은 에러 응답을 반환할 수 있습니다:

```json
{
  "detail": "에러 메시지"
}
```

### 주요 에러 코드
- `400`: 잘못된 요청
- `500`: 서버 내부 오류
- `503`: 서비스 사용 불가

## 사용 예시

### cURL 예시

```bash
# 문제 생성
curl -X POST "http://localhost:8000/api/v1/generate-question-with-rag" \
  -H "Content-Type: application/json" \
  -d '{
    "userId": 123,
    "bookId": 456,
    "pdf_base64": "your_pdf_base64_data",
    "query": "Java 변수와 데이터 타입에 대한 문제를 만들어주세요",
    "difficulty": "보통",
    "question_type": "객관식",
    "max_pages": 5
  }'

# 개념 설명
curl -X POST "http://localhost:8000/api/v1/present-concept-explanation" \
  -H "Content-Type: application/json" \
  -d '{
    "userId": 123,
    "bookId": 456,
    "pdf_base64": "your_pdf_base64_data",
    "concept_query": "Java 클래스와 객체에 대해 설명해주세요",
    "user_level": "초급",
    "max_pages": 5
  }'
```

### Python 예시

```python
import requests
import base64

# PDF 파일을 Base64로 인코딩
with open("sample.pdf", "rb") as pdf_file:
    pdf_base64 = base64.b64encode(pdf_file.read()).decode()

# 문제 생성 요청
response = requests.post(
    "http://localhost:8000/api/v1/generate-question-with-rag",
    json={
        "userId": 123,
        "bookId": 456,
        "pdf_base64": pdf_base64,
        "query": "Java 변수와 데이터 타입에 대한 문제를 만들어주세요",
        "difficulty": "보통",
        "question_type": "객관식",
        "max_pages": 5
    }
)

print(response.json())
```

## 성능 최적화

1. **캐싱**: PDF 처리 결과는 캐시되어 재사용됩니다.
2. **청킹**: 의미적 청킹으로 정확한 컨텍스트를 제공합니다.
3. **벡터 검색**: Elasticsearch를 사용한 빠른 유사도 검색
4. **병렬 처리**: 여러 청크를 동시에 처리합니다.

## 제한사항

1. **PDF 크기**: 대용량 PDF는 처리 시간이 오래 걸릴 수 있습니다.
2. **메모리 사용량**: 임베딩 생성 시 메모리를 많이 사용합니다.
3. **API 호출 제한**: OpenAI API 호출 제한이 있을 수 있습니다.

## 환경 설정

필요한 환경 변수:
```bash
OPENAI_API_KEY=your_openai_api_key
ELASTICSEARCH_HOSTS=http://localhost:9200
```

## 지원

문제가 발생하면 다음을 확인하세요:
1. 서버가 실행 중인지 확인
2. 환경 변수가 올바르게 설정되었는지 확인
3. Elasticsearch가 실행 중인지 확인
4. PDF 파일이 올바른 형식인지 확인 