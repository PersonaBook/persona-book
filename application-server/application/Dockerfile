# 1단계: 빌드 스테이지
FROM gradle:8.5-jdk17-alpine AS build

USER root
ENV GRADLE_USER_HOME=/workspace/.gradle

WORKDIR /workspace
COPY . .

# 테스트 생략
RUN gradle bootJar -x test --no-daemon

# 2단계: 실행 스테이지
FROM openjdk:17-jdk-alpine

WORKDIR /app
COPY --from=build /workspace/build/libs/*.jar app.jar

ENTRYPOINT ["java", "-jar", "app.jar"]
