package com.example.application.config;

import com.example.application.entity.User;
import com.example.application.entity.VerificationToken;
import com.example.application.repository.UserRepository;
import com.example.application.repository.VerificationTokenRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.boot.CommandLineRunner;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.Optional;
import java.util.Random;

@Configuration
@RequiredArgsConstructor
public class SampleDataInitializer {

    private final UserRepository userRepository;
    private final VerificationTokenRepository verificationTokenRepository;

    private final BCryptPasswordEncoder passwordEncoder = new BCryptPasswordEncoder();

    @Bean
    public CommandLineRunner initSampleUser() {
        return args -> {
            String email = "test@example.com";
            String userName = "테스트유저";

            if (userRepository.findByUserEmail(email).isEmpty()) {
                User testUser = User.builder()
                        .userName(userName)
                        .userEmail(email)
                        .userPhoneNumber("01012345678")
                        .userBirthDate(LocalDate.of(2000, 1, 1))
                        .userJob("학생")
                        .password(passwordEncoder.encode("test1234!"))
                        .build();

                User savedUser = userRepository.save(testUser);
                System.out.println("✅ 테스트 계정 생성 완료: " + email + " / test1234!");

                // 이메일 인증 토큰 생성 (실제 이메일은 보내지 않음)
                String verificationCode = generateVerificationCode();
                VerificationToken token = new VerificationToken(verificationCode, savedUser);
                verificationTokenRepository.save(token);
                System.out.println("📮 테스트용 인증 코드 생성: " + verificationCode + " (DB에 저장됨)");
            }
        };
    }

    private String generateVerificationCode() {
        Random random = new Random();
        int code = 100000 + random.nextInt(900000);
        return String.valueOf(code);
    }
}
