package com.example.application.domain.auth.service;

import com.example.application.domain.auth.dto.request.LoginRequestDto;
import com.example.application.domain.auth.dto.request.RegisterRequestDto;
import com.example.application.domain.auth.dto.response.LoginResponseDto;
import com.example.application.domain.user.entity.User;
import com.example.application.domain.user.repositroy.UserRepository;
import com.example.application.global.exception.CustomException;
import com.example.application.global.exception.ErrorCode;
import com.example.application.global.security.util.JwtProvider;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.Map;
import java.util.Random;
import java.util.concurrent.ConcurrentHashMap;

@Service
@Slf4j
@RequiredArgsConstructor
@Transactional(readOnly = true)
public class AuthService {

    private final Map<String, VerificationInfo> memoryVerificationStore = new ConcurrentHashMap<>();
    private static final int VERIFICATION_CODE_EXPIRY_MINUTES = 5;

    private final PasswordEncoder passwordEncoder;
    private final UserRepository userRepository;
    private final JwtProvider jwtProvider;
    private final EmailService emailService;

    private static class VerificationInfo {
        private final String code;
        private final LocalDateTime expiryTime;

        public VerificationInfo(String code, int minutes) {
            this.code = code;
            this.expiryTime = LocalDateTime.now().plusMinutes(minutes);
        }

        public boolean isValid(String inputCode) {
            return this.code.equals(inputCode) && LocalDateTime.now().isBefore(this.expiryTime);
        }
    }

    @Transactional
    public LoginResponseDto login(LoginRequestDto request) {
        User user = userRepository.findByEmail(request.getEmail())
                .orElseThrow(() -> new CustomException(ErrorCode.USER_NOT_FOUND));

        if (!passwordEncoder.matches(request.getPassword(), user.getPassword())) {
            throw new CustomException(ErrorCode.INVALID_PASSWORD);
        }

        return issueTokens(user);
    }

    public LoginResponseDto refreshToken(String refreshToken) {
        if (refreshToken == null || !jwtProvider.isValidToken(refreshToken)) {
            throw new CustomException(ErrorCode.INVALID_TOKEN);
        }

        Long userId = jwtProvider.getUserId(refreshToken);
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new CustomException(ErrorCode.USER_NOT_FOUND));

        return issueTokens(user);
    }

    private LoginResponseDto issueTokens(User user) {
        String accessToken = jwtProvider.createAccessToken(user.getUserId(), user.getEmail());
        String refreshToken = jwtProvider.createRefreshToken(user.getUserId(), user.getEmail());

        return LoginResponseDto.builder()
                .accessToken(accessToken)
                .refreshToken(refreshToken)
                .userId(user.getUserId())
                .name(user.getName())
                .email(user.getEmail())
                .build();
    }

    public void logout(String refreshToken) {
        // Stateless 방식이므로 서버에서 특별히 할 일은 없음 (로그만 남김)
        // Redis를 쓴다면 여기서 Redis의 RefreshToken을 삭제해야 함
        log.info("로그아웃 처리됨 (클라이언트 토큰 폐기)");
    }

    @Transactional
    public void register(RegisterRequestDto request) {
        if (userRepository.existsByName(request.getName()) || userRepository.existsByEmail(request.getEmail())) {
            throw new CustomException(ErrorCode.DUPLICATE_USER);
        }

        User user = User.builder()
                .name(request.getName())
                .email(request.getEmail())
                .password(passwordEncoder.encode(request.getPassword()))
                .birthDate(request.getBirthDate())
                .job(request.getJob())
                .phoneNumber(request.getPhoneNumber())
                .build();

        userRepository.save(user);

        sendVerificationCode(request.getEmail());
    }

    public String findId(String name, String email) {
        return userRepository.findByNameAndEmail(name, email)
                .map(User::getEmail)
                .orElseThrow(() -> new CustomException(ErrorCode.USER_NOT_FOUND));
    }

    @Transactional
    public void resetPassword(String name, String email, String newPassword) {
        User user = userRepository.findByNameAndEmail(name, email)
                .orElseThrow(() -> new CustomException(ErrorCode.USER_NOT_FOUND));

        user.resetPassword(passwordEncoder.encode(newPassword));
    }

    public void sendVerificationCode(String email) {
        String verificationCode = createVerificationCode();

        memoryVerificationStore.put(email, new VerificationInfo(verificationCode, VERIFICATION_CODE_EXPIRY_MINUTES));

        try {
            String subject = "이메일 인증 코드";
            String text = "인증 코드는 " + verificationCode + " 입니다.";
            emailService.sendEmail(email, subject, text);
        } catch (Exception e) {
            memoryVerificationStore.remove(email);
            log.error("이메일 발송 실패: {}", email, e);
            throw new CustomException(ErrorCode.EMAIL_SEND_FAILED);
        }
    }

    public void verifyCode(String email, String inputCode) {
        VerificationInfo info = memoryVerificationStore.get(email);

        if (info == null) {
            throw new CustomException(ErrorCode.INVALID_AUTH_CODE); // 요청 기록 없음
        }

        if (!info.isValid(inputCode)) {
            throw new CustomException(ErrorCode.INVALID_AUTH_CODE); // 코드 틀림 or 만료됨
        }

        memoryVerificationStore.remove(email);
    }

    private String createVerificationCode() {
        return String.valueOf(100000 + new Random().nextInt(900000));
    }
}