# LangChain RAG Server

AI 기반 교육용 질문 생성 및 답변 분석을 위한 FastAPI 서버입니다.

## 주요 기능

- **질문 생성**: LangChain과 Elasticsearch를 활용한 교육용 질문 생성
- **개념 설명**: 개인화된 수준에 맞는 개념 설명 생성

## 기술 스택

- **FastAPI**: 웹 프레임워크
- **LangChain**: AI 체인 및 프롬프트 관리
- **OpenAI**: LLM 서비스
- **Elasticsearch**: 벡터 저장소 및 검색
- **Poetry**: 의존성 관리

## 설치 및 실행
>
> docker-compose 없이 elasticsearch만 별도로 띄워 개발할 경우

### 1. 의존성 설치

```bash
poetry install
```

### 2. 환경 변수 설정

```bash
.env.dev에 ELASTICSEARCH_HOSTS 값 수정

ELASTICSEARCH_HOSTS=http://localhost:9200
```

### 3. Elasticsearch 실행

```bash
docker build -t custom-elasticsearch-nori -f Dockerfile.elasticsearch .

docker run -d --name elasticsearch \
  -p 9200:9200 -p 9300:9300 \
  -e "discovery.type=single-node" \
  -e "xpack.security.enabled=false" \
  custom-elasticsearch-nori
```

### 4. 서버 실행

```bash
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## 개발 환경 설정 (VS Code)

### Poetry 가상환경 설정

1. **의존성 설치 및 가상환경 생성**

   ```bash
   poetry install
   ```

2. **현재 사용 중인 가상환경 확인**

   ```bash
   poetry env info
   ```

   출력 예시:

   ```text
   Virtualenv
   Python:         3.12.1
   Path:           C:\Users\***\virtualenvs\langchain-server-xxx-py3.12
   ```

3. **VS Code에서 해당 가상환경을 명시적으로 선택**
   - `Ctrl+Shift+P` → "Python: Select Interpreter"
   - 목록에 안 보이면 "Enter interpreter path" 클릭
   - 위에서 확인한 경로로 이동:

     ```text
     C:\Users\***\virtualenvs\langchain-server-xxx-py3.12\Scripts\python.exe
     ```

4. **추가 조치**
   - `Ctrl+Shift+P` → "Developer: Reload Window"
   - `Ctrl+Shift+P` → "Python: Restart Language Server"

이렇게 설정하면 VS Code가 해당 가상환경을 기반으로 lint, jump-to-definition 등이 정상 작동합니다.

## pre-commit 사용법
>
> 커밋 전에 코드 스타일 검사, 린트, 포맷팅 등을 자동으로 실행해주는 도구입니다

```text
# Git 훅을 설치하여 커밋 시 자동으로 검사 실행
pre-commit install

# 모든 파일에 대해 수동으로 훅을 실행할 때 사용
pre-commit run --all-files
```

## API 문서

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 환경 변수

| 변수명 | 설명 | 기본값 |
|--------|------|--------|
| `OPENAI_API_KEY` | OpenAI API 키 | 필수 |
| `OPENAI_MODEL_NAME` | 사용할 모델명 | gpt-4 |
| `ELASTICSEARCH_HOSTS` | Elasticsearch 호스트 목록 | localhost:9200 |
| `APP_ENV` | 애플리케이션 환경 | development |
| `DEBUG` | 디버그 모드 | True |

## 프로젝트 구조

```text
langchain-server/
├── app/
│   ├── api/                # API 엔드포인트
│   ├── core/               # 설정 및 공통 모듈
│   │   ├── config.py       # 환경 변수 설정
│   │   └── elasticsearch_client.py  # Elasticsearch 클라이언트
│   ├── entity/             # 도메인 모델 (@dataclass)
│   ├── repository/         # 데이터 접근 계층 (Persistence)
│   ├── schemas/            # API 입출력용 Pydantic 모델
│   │   ├── request/        # API 요청 스키마
│   │   └── response/       # API 응답 스키마
│   ├── services/           # 유즈케이스 / 비즈니스 로직
│   └── main.py            # FastAPI 진입점
├── tests/                 # 테스트 코드
├── pyproject.toml         # Poetry 설정
├── env.example            # 환경 변수 예시
├── Dockerfile             # Docker 설정
└── README.md              # 프로젝트 문서
```
