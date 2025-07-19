# 1. JDK 기반 이미지 사용 (경량 Alpine 버전)
FROM openjdk:17-jdk-alpine

# 2. 작업 디렉토리 설정
WORKDIR /app

# 3. build/libs 디렉토리 내의 jar 파일 복사
ARG JAR_FILE=build/libs/*.jar
COPY ${JAR_FILE} app.jar

# 4. 실행 명령
ENTRYPOINT ["java", "-jar", "app.jar"]