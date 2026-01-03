package com.example.application.global.init;

import com.example.application.domain.user.entity.User;
import com.example.application.domain.user.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.boot.CommandLineRunner;
import org.springframework.context.annotation.Profile;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Component;

import java.time.LocalDate;

@Component
@RequiredArgsConstructor
@Profile("dev")
@Slf4j
public class SampleDataInitializer implements CommandLineRunner {

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;

    private static final String TEST_EMAIL = "test@example.com";
    private static final String TEST_PASSWORD = "test1234!";

    @Override
    public void run(String... args) {
        if (userRepository.findByEmail(TEST_EMAIL).isPresent()) {
            log.info("이미 테스트 계정이 존재합니다. 초기화를 건너뜁니다.");
            return;
        }

        createTestUser();
    }

    private void createTestUser() {
        User testUser = User.builder()
                .name("테스트유저")
                .email(TEST_EMAIL)
                .password(passwordEncoder.encode(TEST_PASSWORD)) // 비밀번호 암호화 필수
                .phoneNumber("01012345678")
                .birthDate(LocalDate.of(2000, 1, 1))
                .job("백엔드 취준생")
                .build();

        userRepository.save(testUser);

        log.info("테스트 계정 생성 완료: ID=[{}] / PW=[{}]", TEST_EMAIL, TEST_PASSWORD);
    }
}