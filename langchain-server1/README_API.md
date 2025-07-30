# Java Learning System API

Java 학습을 위한 AI 기반 문제 생성 및 평가 시스템의 FastAPI 서버입니다.

## 🚀 빠른 시작

### 1. 환경 설정

```bash
# 의존성 설치
pip install -r requirements.txt

# 환경 변수 설정 (.env 파일 생성)
echo "OPENAI_API_KEY=your_api_key_here" > .env

# Java 교재 PDF 파일을 현재 디렉토리에 복사
cp /path/to/your/java_textbook.pdf .
```

### 2. 서버 시작

```bash
# 방법 1: 실행 스크립트 사용 (권장)
python run_server.py

# 방법 2: 직접 실행
python fastapi_server.py

# 방법 3: uvicorn 직접 사용
uvicorn fastapi_server:app --host 0.0.0.0 --port 8000 --reload
```

### 3. API 테스트

```bash
# API 테스트 실행
python test_api_client.py
```

## 📋 API 엔드포인트

### 기본 정보
- **Base URL**: `http://localhost:8000`
- **API 문서**: `http://localhost:8000/docs`
- **대안 문서**: `http://localhost:8000/redoc`

### 엔드포인트 목록

#### 1. 서버 상태 확인
```
GET /health
```

#### 2. 문제 생성
```
POST /generate_question
```
**요청 본문:**
```json
{
  "context": "Java에서 변수는 데이터를 저장하는 메모리 공간입니다.",
  "difficulty": "보통",
  "topic": "변수",
  "question_type": "개념이해"
}
```

#### 3. 답변 평가
```
POST /evaluate_answer
```
**요청 본문:**
```json
{
  "question": {...},
  "user_answer": 1,
  "is_correct": true,
  "concept_keywords": ["변수", "데이터타입"]
}
```

#### 4. 개념 설명
```
POST /explain_concept
```
**요청 본문:**
```json
{
  "concept_keyword": "변수",
  "wrong_answer_context": "사용자가 변수 개념을 잘못 이해함"
}
```

#### 5. 개념 재설명
```
POST /reexplain_concept
```
**요청 본문:**
```json
{
  "concept_keyword": "변수",
  "user_feedback": "더 자세한 예제가 필요합니다"
}
```

#### 6. 페이지 검색
```
POST /search_pages
```
**요청 본문:**
```json
{
  "keyword": "변수"
}
```

#### 7. 키워드 목록 조회
```
GET /keywords
```

#### 8. 챕터 정보 조회
```
GET /chapters
```

## 🔧 사용 예제

### Python 클라이언트 예제

```python
import requests

# 서버 상태 확인
response = requests.get("http://localhost:8000/health")
print(response.json())

# 문제 생성
question_data = {
    "context": "Java에서 변수는 데이터를 저장하는 메모리 공간입니다.",
    "difficulty": "보통",
    "topic": "변수",
    "question_type": "개념이해"
}

response = requests.post("http://localhost:8000/generate_question", json=question_data)
question = response.json()
print(question)

# 답변 평가
evaluation_data = {
    "question": question["question"],
    "user_answer": 1,
    "is_correct": True,
    "concept_keywords": ["변수", "데이터타입"]
}

response = requests.post("http://localhost:8000/evaluate_answer", json=evaluation_data)
evaluation = response.json()
print(evaluation)
```

### cURL 예제

```bash
# 서버 상태 확인
curl -X GET "http://localhost:8000/health"

# 문제 생성
curl -X POST "http://localhost:8000/generate_question" \
  -H "Content-Type: application/json" \
  -d '{
    "context": "Java에서 변수는 데이터를 저장하는 메모리 공간입니다.",
    "difficulty": "보통",
    "topic": "변수",
    "question_type": "개념이해"
  }'

# 키워드 검색
curl -X POST "http://localhost:8000/search_pages" \
  -H "Content-Type: application/json" \
  -d '{"keyword": "변수"}'
```

## 📁 파일 구조

```
langchain-server1/
├── main.py                    # 기존 콘솔 애플리케이션
├── fastapi_server.py          # FastAPI 서버
├── test_api_client.py         # API 테스트 클라이언트
├── run_server.py              # 서버 실행 스크립트
├── requirements.txt           # 의존성 목록
├── config.json               # 설정 파일
├── keywords.json             # 키워드 데이터
├── user_fewshot_examples.json # Few-shot 예제
├── core/                     # 핵심 모듈
│   ├── state_machine.py      # 상태 머신
│   ├── models.py             # 모델 관리
│   ├── vector_store.py       # 벡터 저장소
│   ├── chains.py             # 체인 팩토리
│   └── concept_explainer.py  # 개념 설명
├── generators/               # 생성기 모듈
│   └── question_generator.py # 문제 생성기
├── analyzers/               # 분석기 모듈
│   └── adaptive_learning.py # 적응형 학습
└── utils/                   # 유틸리티
    └── file_manager.py      # 파일 관리
```

## ⚠️ 주의사항

1. **OpenAI API 키**: `.env` 파일에 유효한 OpenAI API 키를 설정해야 합니다.
2. **PDF 파일**: Java 교재 PDF 파일이 현재 디렉토리에 있어야 합니다.
3. **메모리**: 벡터 저장소 초기화에 시간이 걸릴 수 있습니다.
4. **네트워크**: 외부에서 접근하려면 방화벽 설정을 확인하세요.

## 🔍 문제 해결

### 서버가 시작되지 않는 경우
1. 의존성 설치 확인: `pip install -r requirements.txt`
2. 환경 변수 확인: `.env` 파일에 API 키 설정
3. PDF 파일 확인: Java 교재 PDF 파일 존재 여부
4. 포트 충돌 확인: 8000번 포트가 사용 중인지 확인

### API 호출이 실패하는 경우
1. 서버 상태 확인: `GET /health`
2. 요청 형식 확인: JSON 형식과 필수 필드
3. 로그 확인: 서버 콘솔 출력 확인

## 📞 지원

문제가 발생하면 다음을 확인해주세요:
1. 서버 로그 확인
2. API 문서 참조: `http://localhost:8000/docs`
3. 테스트 클라이언트 실행: `python test_api_client.py` 