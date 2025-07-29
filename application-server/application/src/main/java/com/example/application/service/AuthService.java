package com.example.application.service;

import com.example.application.entity.User;
import com.example.application.entity.VerificationToken;

import com.example.application.dto.auth.request.LoginRequest;
import com.example.application.dto.auth.request.SignupRequest;
import com.example.application.dto.auth.response.JwtResponse;
import com.example.application.dto.auth.response.UserProfileResponse;
import com.example.application.repository.UserRepository;
import com.example.application.repository.VerificationTokenRepository;

import com.example.application.security.jwt.JwtTokenProvider;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.time.LocalDateTime;
import com.example.application.exception.InvalidVerificationCodeException;
import com.example.application.exception.UserNotFoundException;

import java.util.Optional;
import java.util.Random;

import jakarta.servlet.http.HttpSession;

@Service
public class AuthService {

    private static final Logger logger = LoggerFactory.getLogger(AuthService.class);

    // 이메일 인증 코드 유지시간
    private static final long VERIFICATION_CODE_EXPIRY_MINUTES = 5; // 5분

    private final BCryptPasswordEncoder passwordEncoder = new BCryptPasswordEncoder();
    private final UserRepository userRepository;
    private final JwtTokenProvider jwtTokenProvider;
    private final EmailService emailService;
    private final VerificationTokenRepository verificationTokenRepository;

    public AuthService(UserRepository userRepository,
                      JwtTokenProvider jwtTokenProvider,
                      EmailService emailService,
                      VerificationTokenRepository verificationTokenRepository) {
        this.userRepository = userRepository;
        this.jwtTokenProvider = jwtTokenProvider;
        this.emailService = emailService;
        this.verificationTokenRepository = verificationTokenRepository;
    }

    

    public JwtResponse authenticateUser(LoginRequest loginRequest, HttpSession session) {
        User user = userRepository.findByUserEmail(loginRequest.getUserEmail())
                .orElseThrow(() -> new UserNotFoundException("User not found with email: " + loginRequest.getUserEmail()));

        if (!passwordEncoder.matches(loginRequest.getPassword(), user.getPassword())) {
            throw new RuntimeException("Invalid password!");
        }

        // rememberMe에 따라 다른 만료시간의 토큰 생성
        String jwt = jwtTokenProvider.generateJwtToken(user.getUserEmail(), loginRequest.isRememberMe());

        // refresh token 생성하고 세션에 저장
        String refreshTokenString = jwtTokenProvider.generateRefreshToken(user.getUserEmail());
        session.setAttribute("refreshToken", refreshTokenString);
        session.setAttribute("rememberMe", loginRequest.isRememberMe());
        session.setAttribute("loginToken", jwt);

        return new JwtResponse(jwt, refreshTokenString, user.getUserId(), user.getUserEmail(), user.getUserEmail());
    }

    public JwtResponse refreshToken(String refreshTokenString, HttpSession session) {
        String storedRefreshToken = (String) session.getAttribute("refreshToken");

        if (storedRefreshToken == null || !storedRefreshToken.equals(refreshTokenString)) {
            throw new RuntimeException("Invalid or expired refresh token");
        }

        String userEmail = jwtTokenProvider.getUserEmailFromRefreshToken(refreshTokenString);
        User user = userRepository.findByUserEmail(userEmail)
                .orElseThrow(() -> new UserNotFoundException("User not found with email: " + userEmail));

        // rememberMe 설정으로 새 액세스 토큰 생성
        Boolean rememberMe = (Boolean) session.getAttribute("rememberMe");
        boolean useRememberMe = rememberMe != null ? rememberMe : false;
        String newAccessToken = jwtTokenProvider.generateJwtToken(user.getUserEmail(), useRememberMe);

        return new JwtResponse(newAccessToken, refreshTokenString, user.getUserId(), user.getUserName(), user.getUserEmail());
    }

    public void logout(HttpSession session) {
        session.removeAttribute("refreshToken");
        session.removeAttribute("rememberMe");
        session.invalidate();
    }

    public void validateAndCleanupSession(HttpSession session) {
        String loginToken = (String) session.getAttribute("loginToken");
        if (loginToken != null && !jwtTokenProvider.validateToken(loginToken)) {
            session.removeAttribute("loginToken");
            session.removeAttribute("refreshToken");
        }
    }

    public boolean registerUser(SignupRequest signUpRequest) {
        if (!validateUserRegistration(signUpRequest)) {
            return false;
        }
        
        User user = createUserFromRequest(signUpRequest);
        userRepository.save(user);
        
        return sendVerificationEmailToNewUser(user);
    }

    private boolean validateUserRegistration(SignupRequest signUpRequest) {
        return !userRepository.existsByUserName(signUpRequest.getUserName()) &&
               !userRepository.existsByUserEmail(signUpRequest.getUserEmail());
    }

    private User createUserFromRequest(SignupRequest signUpRequest) {
        User user = new User();
        user.setUserName(signUpRequest.getUserName());
        user.setUserEmail(signUpRequest.getUserEmail());
        user.setPassword(passwordEncoder.encode(signUpRequest.getPassword()));
        user.setUserBirthDate(signUpRequest.getBirthDate());
        user.setUserJob(signUpRequest.getJob());
        user.setUserPhoneNumber(signUpRequest.getUserPhoneNumber());
        return user;
    }

    private boolean sendVerificationEmailToNewUser(User user) {
        String verificationCode = generateVerificationCode();
        VerificationToken verificationToken = new VerificationToken(verificationCode, user);
        verificationTokenRepository.save(verificationToken);

        try {
            emailService.sendVerificationEmail(user.getUserEmail(), verificationCode);
            return true;
        } catch (Exception e) {
            logger.error("Failed to send verification email to {}: {}", user.getUserEmail(), e.getMessage());
            return false;
        }
    }



    public UserProfileResponse getUserProfile(Long userId) {
        Optional<User> userOptional = userRepository.findById(userId);
        if (userOptional.isPresent()) {
            User user = userOptional.get();
            return new UserProfileResponse(user.getUserId(), user.getUserName(), user.getUserEmail(), user.getUserBirthDate(), user.getUserJob());
        }
        return null;
    }

    public String findUsernameByEmail(String email) {
        Optional<User> userOptional = userRepository.findByUserEmail(email);
        return userOptional.map(User::getUserEmail).orElse(null);
    }

    @Transactional
    public void resetPassword(String userName, String email, String verificationCode, String newPassword) {
        verifyVerificationCode(email, verificationCode);

        User user = userRepository.findByUserNameAndUserEmail(userName, email)
                .orElseThrow(() -> new UserNotFoundException("이름과 이메일이 일치하지 않습니다."));

        user.setPassword(passwordEncoder.encode(newPassword));
        userRepository.save(user);
        verificationTokenRepository.deleteByEmail(email);
    }

    private String generateVerificationCode() {
        Random random = new Random();
        int code = 100000 + random.nextInt(900000);
        return String.valueOf(code);
    }

    public boolean forgotPassword(String email) {
        String result = sendEmailVerificationCode(email, true);
        return "인증번호를 발송했습니다.".equals(result); // 성공 메시지면 성공
    }

    @Transactional
    public void verifyVerificationCode(String email, String code) {
        VerificationToken verificationToken = verificationTokenRepository.findByEmail(email);

        if (verificationToken == null || !verificationToken.getToken().equals(code)) {
            throw new InvalidVerificationCodeException("Invalid verification code.");
        }

        if (verificationToken.getExpiryDate().isBefore(LocalDateTime.now())) {
            verificationTokenRepository.delete(verificationToken);
            throw new InvalidVerificationCodeException("Verification code has expired.");
        }
    }

    @Transactional
    public boolean verifyEmailCode(String email, String code) {
        try {
            verifyVerificationCode(email, code);
            // 인증번호는 여기서 삭제하지 않음. 최종 동작(비밀번호 변경 등)에서만 삭제
            return true;
        } catch (InvalidVerificationCodeException e) {
            logger.warn("Email verification failed for {}: {}", email, e.getMessage());
            return false;
        }
    }

    @Transactional
    public String sendEmailVerificationCode(String email, boolean mustExist) {
        String validationResult = validateEmailForVerification(email, mustExist);
        if (!"VALID".equals(validationResult)) {
            return validationResult;
        }
        
        return processVerificationCodeSending(email);
    }

    private String validateEmailForVerification(String email, boolean mustExist) {
        if (mustExist) {
            // 이메일이 반드시 존재해야 함 (id/pw찾기, 마이페이지)
            if (!userRepository.existsByUserEmail(email)) {
                logger.warn("Email {} does not exist. Cannot send verification code.", email);
                return "해당 이메일로 가입된 계정이 없습니다.";
            }
        } else {
            // 이메일이 존재하면 안 됨 (회원가입)
            if (userRepository.existsByUserEmail(email)) {
                logger.warn("Email {} already exists. Cannot send verification code.", email);
                return "이미 가입된 이메일입니다.";
            }
        }
        return "VALID";
    }

    private String processVerificationCodeSending(String email) {
        try {
            String verificationCode = generateVerificationCode();
            saveOrUpdateVerificationToken(email, verificationCode);
            emailService.sendEmail(email, "Email Verification Code", "Your verification code is: " + verificationCode);
            return "인증번호를 발송했습니다.";
        } catch (Exception e) {
            logger.error("Failed to send email verification code to {}: {}", email, e.getMessage());
            return "이메일 발송 중 오류가 발생했습니다.";
        }
    }

    private void saveOrUpdateVerificationToken(String email, String verificationCode) {
        VerificationToken existingToken = verificationTokenRepository.findByEmail(email);
        
        if (existingToken != null) {
            existingToken.setToken(verificationCode);
            existingToken.setExpiryDate(LocalDateTime.now().plusMinutes(VERIFICATION_CODE_EXPIRY_MINUTES));
            verificationTokenRepository.save(existingToken);
        } else {
            VerificationToken newToken = new VerificationToken(verificationCode, email);
            verificationTokenRepository.save(newToken);
        }
    }
}