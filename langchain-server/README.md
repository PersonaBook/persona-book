# LangChain RAG Server

AI 기반 교육용 질문 생성 및 답변 분석을 위한 FastAPI 서버입니다.

## 주요 기능

- **질문 생성**: LangChain과 Elasticsearch를 활용한 교육용 질문 생성
- **답변 분석**: 사용자 답변에 대한 AI 기반 분석 및 피드백 제공
- **개념 설명**: 개인화된 수준에 맞는 개념 설명 생성
- **RAG 질의응답**: 검색 기반 질의응답 시스템

## 기술 스택

- **FastAPI**: 웹 프레임워크
- **LangChain**: AI 체인 및 프롬프트 관리
- **OpenAI**: LLM 서비스
- **Elasticsearch**: 벡터 저장소 및 검색
- **Poetry**: 의존성 관리

## 설치 및 실행

### 1. 의존성 설치

```bash
poetry install
```

### 2. 환경 변수 설정

```bash
cp env.example .env
# .env 파일을 편집하여 필요한 API 키와 설정을 입력
```

### 3. 서버 실행

```bash
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## API 엔드포인트


## API 문서

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 환경 변수

| 변수명 | 설명 | 기본값 |
|--------|------|--------|
| `OPENAI_API_KEY` | OpenAI API 키 | 필수 |
| `OPENAI_MODEL_NAME` | 사용할 모델명 | gpt-4 |
| `ELASTICSEARCH_HOST` | Elasticsearch 호스트 | localhost |
| `ELASTICSEARCH_PORT` | Elasticsearch 포트 | 9200 |
| `APP_ENV` | 애플리케이션 환경 | development |
| `DEBUG` | 디버그 모드 | True |

## 개발 가이드

### 프로젝트 구조

```
langchain-server/
├── app/
│   ├── api/           # API 엔드포인트
│   ├── core/          # 설정 및 공통 모듈
│   ├── schemas/       # Pydantic 스키마
│   ├── services/      # 비즈니스 로직
│   └── main.py        # 애플리케이션 진입점
├── tests/             # 테스트 코드
├── pyproject.toml     # Poetry 설정
```