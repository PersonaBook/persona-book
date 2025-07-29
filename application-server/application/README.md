# 🌱 Spring Boot 기반 Application 서버

> FastAPI + LangChain 기반 AI 학습 도우미 시스템의 사용자 API 및 View 제공 서버  
> ✅ 사용자 인증, PDF 뷰어, 노트 관리, 챗봇 메시지 처리, 상태 기반 흐름 제어 담당

---

## 📁 디렉토리 구조

```plaintext
📦 application-server/application/
└─ 📁 src/
   └─ 📁 main/
      └─ 📁 java/
         └─ com.example.application/
            ├─ 📁 config/           # 보안 및 글로벌 설정 (CORS, JWT, 인터셉터 등)
            ├─ 📁 controller/       # API 및 View 컨트롤러
            │  ├─ 📁 auth/          # 로그인, 회원가입 등 인증 관련
            │  ├─ 📁 chat/          # 챗봇 메시지 처리
            │  ├─ 📁 note/          # 노트 CRUD 및 연동
            │  ├─ 📁 pdf/           # PDF 뷰어 처리
            │  ├─ 📁 user/          # 사용자 정보 관련
            │  └─ HomeViewController.java
            ├─ 📁 dto/              # 요청/응답 DTO 계층
            ├─ 📁 entity/           # JPA 엔티티 정의
            ├─ 📁 exception/        # 공통 예외 처리
            ├─ 📁 repository/       # Spring Data JPA Repository
            ├─ 📁 security/         # JWT 필터, 인가 처리 등 보안 로직
            ├─ 📁 service/          # 도메인별 비즈니스 로직
            ├─ 📁 util/             # 유틸리티 클래스
            └─ Application.java     # 메인 실행 클래스
```

---

## 📌 핵심 역할

| 기능 구분     | 설명                                                      |
| --------- | ------------------------------------------------------- |
| 📘 사용자 인증 | 회원가입, 로그인, JWT 발급 및 검증 처리 (`auth`)                      |
| 📄 PDF 뷰어 | 사용자가 업로드한 PDF 문서를 뷰어로 렌더링 (`pdf`)                       |
| 📝 노트 관리  | 사용자가 작성한 노트 CRUD 처리 및 DB 저장 (`note`)                    |
| 💬 챗봇 처리  | 사용자 질문 → 상태 기반 흐름 판단 → FastAPI 호출 후 AI 응답 반환 (`chat`)   |
| 🧠 상태 흐름  | 상태 기반 챗봇 시나리오 관리, Stage/FeatureContext 저장 및 전이 (`chat`) |
| 🔐 보안 설정  | JWT 필터 체인, 사용자 인증 필터, CORS 설정 등 (`security/config`)     |

---

## 🔁 챗봇 서비스 흐름

```plaintext
[사용자 입력]
   ↓
[Spring ChatService: 상태 판단 + 흐름 제어]
   ↓                     ↘️
[상태 전이에 따른 로직 처리]  → (필요 시) [FastAPI (/chat)] 호출
   ↓
[다음 상태 + 메시지 결정]
   ↓
[ChatHistory 저장 + 응답 반환]
```

---

## ⚙️ 기술 스택

| 구성 요소  | 기술                     |
| ------ | ---------------------- |
| 프레임워크  | Spring Boot 3.x        |
| 언어     | Java 17                |
| 뷰 엔진   | Thymeleaf              |
| 빌드 도구  | Gradle                 |
| 보안     | Spring Security + JWT  |
| API 통신 | WebClient (FastAPI 호출) |
| 데이터베이스 | MySQL 8.0              |
| 문서 검색  | Elasticsearch 8.x      |

---

## ⚙️ 환경 설정 주의사항

이 프로젝트는 기본적으로 Docker 기반 실행을 전제로 구성되어 있으며, `application.yml` 내부의 DB 및 이메일 설정 또한 Docker 환경에 맞추어 작성되어 있습니다.

### ❗ Spring Boot 단독 실행 시 주의

Spring Boot만 로컬에서 단독으로 실행하려면 `application.yml`의 다음 항목을 반드시 로컬 개발환경에 맞게 수정해야 합니다:

### 🔧 수정이 필요한 설정 예시

```yaml
spring:
  datasource:
    url: jdbc:mysql://127.0.0.1:3306/<DB 이름>
    username: <사용자명>
    password: <비밀번호>
```

>현재는 `.env.dev`, `.env.prod` 기반으로 `SPRING_DATASOURCE_URL` 등이 Docker 네트워크 상의 컨테이너 이름(mysql 등)으로 구성되어 있으므로, 단독 실행 시에는 명시적인 localhost 주소로 직접 수정해야 정상적으로 실행됩니다.