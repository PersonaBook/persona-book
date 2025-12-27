package com.example.application.domain.auth.service;

import com.example.application.domain.user.entity.User;
import com.example.application.domain.auth.entity.VerificationToken;

import com.example.application.domain.auth.dto.request.LoginRequestDto;
import com.example.application.domain.auth.dto.request.RegisterRequestDto;
import com.example.application.domain.auth.dto.response.LoginResponseDto;
import com.example.application.domain.auth.dto.response.UserProfileResponseDto;
import com.example.application.domain.user.repositroy.UserRepository;
import com.example.application.domain.auth.repository.VerificationTokenRepository;

import com.example.application.global.security.jwt.JwtTokenProvider;
import lombok.extern.slf4j.Slf4j;
import lombok.RequiredArgsConstructor;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import com.example.application.global.exception.InvalidVerificationCodeException;
import com.example.application.global.exception.UserNotFoundException;

import java.util.Random;

import jakarta.servlet.http.HttpSession;

@Service
@Slf4j
@RequiredArgsConstructor
@Transactional(readOnly = true)
public class AuthService {

    // 이메일 인증 코드 유지시간
    private static final long VERIFICATION_CODE_EXPIRY_MINUTES = 5; // 5분

    private final BCryptPasswordEncoder passwordEncoder = new BCryptPasswordEncoder();

    private final UserRepository userRepository;
    private final JwtTokenProvider jwtTokenProvider;
    private final EmailService emailService;
    private final VerificationTokenRepository verificationTokenRepository;

    // =================================================================================
    // 1. 로그인 & 토큰 관리
    // =================================================================================

    @Transactional
    public LoginResponseDto login(LoginRequestDto loginRequestDto, HttpSession session) {
        User user = userRepository.findByEmail(loginRequestDto.getEmail())
                .orElseThrow(() -> new UserNotFoundException("User not found with email: " + loginRequestDto.getEmail()));

        if (!passwordEncoder.matches(loginRequestDto.getPassword(), user.getPassword())) {
            throw new RuntimeException("Invalid password!");
        }

        return issueTokens(user, loginRequestDto.isAutoLogin(), session);
    }

    public LoginResponseDto refreshToken(String refreshToken, HttpSession session) {
        String storedRefreshToken = (String) session.getAttribute("refreshToken");

        if (storedRefreshToken == null || !storedRefreshToken.equals(refreshToken)) {
            throw new RuntimeException("Invalid or expired refresh token");
        }

        String email = jwtTokenProvider.getUserEmailFromRefreshToken(refreshToken);
        User user = userRepository.findByEmail(email)
                .orElseThrow(() -> new UserNotFoundException("User not found with email: " + email));

        boolean isAutoLogin = Boolean.TRUE.equals(session.getAttribute("autoLogin"));

        return issueTokens(user, isAutoLogin, session);
    }

    /**
     * [Helper] 토큰 발급 및 세션 저장 공통 로직
     */
    private LoginResponseDto issueTokens(User user, boolean isAutoLogin, HttpSession session) {
        String accessToken = jwtTokenProvider.generateJwtToken(user.getEmail(), isAutoLogin);
        String refreshToken = jwtTokenProvider.generateRefreshToken(user.getEmail());

        session.setAttribute("refreshToken", refreshToken);
        session.setAttribute("autoLogin", isAutoLogin);
        session.setAttribute("loginToken", accessToken); // 변수명 통일 필요 (accessToken vs loginToken)

        return new LoginResponseDto(accessToken, refreshToken, user.getUserId(), user.getName(), user.getEmail());
    }

    public void logout(HttpSession session) {
        session.removeAttribute("refreshToken");
        session.removeAttribute("autoLogin");
        session.invalidate();
    }

    // =================================================================================
    // 2. 회원가입 & 프로필
    // =================================================================================

    @Transactional
    public void register(RegisterRequestDto registerRequestDto) {
        if (userRepository.existsByName(registerRequestDto.getName()) || userRepository.existsByEmail(registerRequestDto.getEmail())) {
            throw new IllegalArgumentException("이미 사용 중인 이름이나 이메일입니다.");
        }

        User user = User.builder()
                .name(registerRequestDto.getName())
                .email(registerRequestDto.getEmail())
                .password(passwordEncoder.encode(registerRequestDto.getPassword()))
                .birthDate(registerRequestDto.getBirthDate())
                .job(registerRequestDto.getJob())
                .phoneNumber(registerRequestDto.getPhoneNumber())
                .build();

        userRepository.save(user);

        sendVerificationCode(user.getEmail());
    }

    public UserProfileResponseDto getUserProfile(Long userId) {
        return userRepository.findById(userId)
                .map(u -> new UserProfileResponseDto(u.getUserId(), u.getName(), u.getEmail(), u.getBirthDate(), u.getJob()))
                .orElseThrow(() -> new UserNotFoundException("사용자를 찾을 수 없습니다."));
    }

    public String findId(String name, String email) {
        return userRepository.findByNameAndEmail(name, email)
                .map(User::getEmail) // 아이디(이메일) 반환
                .orElseThrow(() -> new UserNotFoundException("일치하는 사용자 정보가 없습니다."));
    }

    @Transactional
    public void resetPassword(String name, String email, String newPassword) {
        User user = userRepository.findByNameAndEmail(name, email)
                .orElseThrow(() -> new UserNotFoundException("사용자를 찾을 수 없습니다."));

        user.setPassword(passwordEncoder.encode(newPassword));
    }


    // =================================================================================
    // 3. 이메일 인증
    // =================================================================================

    /**
     * [Public] 인증 코드 요청 (검증 + 발송 통합)
     * - Controller에서 호출
     */
    @Transactional
    public void requestVerificationCode(String email, boolean mustExist) {
        boolean exists = userRepository.existsByEmail(email);

        if (mustExist && !exists) {
            throw new UserNotFoundException("해당 이메일로 가입된 계정이 없습니다.");
        }
        if (!mustExist && exists) {
            throw new IllegalArgumentException("이미 가입된 이메일입니다.");
        }

        sendVerificationCode(email);
    }

    /**
     * [Private] 실제 인증 코드 생성 -> 메일 발송
     */
    private void sendVerificationCode(String email) {
        String code = generateRandomCode();

        // DB에 저장된 토큰 조회 (이메일 기준)
        VerificationToken tokenEntity = verificationTokenRepository.findByEmail(email);

        if (tokenEntity == null) {
            // 없으면 새로 생성 (VerificationToken(String code, String email) 생성자 필요)
            tokenEntity = new VerificationToken(code, email);
        } else {
            // 있으면 업데이트
            tokenEntity.setToken(code);
            tokenEntity.setExpiryDate(LocalDateTime.now().plusMinutes(VERIFICATION_CODE_EXPIRY_MINUTES));
        }

        verificationTokenRepository.save(tokenEntity);

        try {
            emailService.sendVerificationEmail(email, code);
        } catch (Exception e) {
            log.error("이메일 발송 실패: {}", email, e);
            throw new RuntimeException("이메일 발송 중 오류가 발생했습니다.");
        }
    }

    /**
     * [Public] 인증 코드 검증
     * - boolean 반환 대신 예외를 던짐 -> Controller에서 try-catch 처리
     */
    @Transactional
    public void verifyEmail(String email, String inputCode) {
        VerificationToken tokenEntity = verificationTokenRepository.findByEmail(email);

        // 1. 토큰 존재 여부 및 코드 일치 확인
        if (tokenEntity == null || !tokenEntity.getToken().equals(inputCode)) {
            throw new InvalidVerificationCodeException("인증 코드가 일치하지 않습니다.");
        }

        // 2. 만료 시간 확인
        if (tokenEntity.getExpiryDate().isBefore(LocalDateTime.now())) {
            verificationTokenRepository.delete(tokenEntity); // 만료된 토큰 삭제
            throw new InvalidVerificationCodeException("인증 코드가 만료되었습니다.");
        }

        // 3. 인증 성공!
        // (필요 시 여기서 토큰을 삭제하거나, 상태를 변경할 수 있음)
        // tokenRepository.delete(tokenEntity);
    }

    private String generateRandomCode() {
        return String.valueOf(100000 + new Random().nextInt(900000));
    }
}