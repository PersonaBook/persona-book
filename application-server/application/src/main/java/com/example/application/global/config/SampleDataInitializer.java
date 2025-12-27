package com.example.application.global.config;

import com.example.application.domain.user.entity.User;
import com.example.application.domain.user.repositroy.UserRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.boot.CommandLineRunner;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.crypto.password.PasswordEncoder;

import java.time.LocalDate;

@Configuration
@RequiredArgsConstructor
public class SampleDataInitializer {

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;

    @Bean
    public CommandLineRunner initSampleUser() {
        return args -> {
            String email = "test@example.com";
            String name = "테스트유저";

            if (userRepository.findByEmail(email).isEmpty()) {
                User testUser = User.builder()
                        .name(name)
                        .email(email)
                        .phoneNumber("01012345678")
                        .birthDate(LocalDate.of(2000, 1, 1))
                        .job("학생")
                        .password(passwordEncoder.encode("test1234!"))
                        .build();

                userRepository.save(testUser);
                System.out.println("✅ 테스트 계정 생성 완료: " + email + " / test1234!");
            }
        };
    }
}
