package com.example.application.service;

import com.example.application.entity.User;
import com.example.application.entity.VerificationToken;

import com.example.application.payload.request.LoginRequest;
import com.example.application.payload.request.SignupRequest;
import com.example.application.payload.response.JwtResponse;
import com.example.application.payload.response.UserProfileResponse;
import com.example.application.repository.UserRepository;
import com.example.application.repository.VerificationTokenRepository;

import com.example.application.security.jwt.JwtTokenProvider;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder; // Import BCryptPasswordEncoder
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.time.Instant;
import java.time.LocalDateTime;
import com.example.application.exception.InvalidVerificationCodeException;
import com.example.application.exception.UserNotFoundException;

import java.time.Duration;
import java.util.Map;
import java.util.Optional;
import java.util.Random;
import java.util.UUID;
import jakarta.servlet.http.HttpSession;
import java.util.concurrent.ConcurrentHashMap;

@Service
public class AuthService {

    private static final Logger logger = LoggerFactory.getLogger(AuthService.class);

    private static final long VERIFICATION_CODE_EXPIRY_MINUTES = 5; // 5분

    @Autowired
    UserRepository userRepository;

    // Directly instantiate BCryptPasswordEncoder
    private final BCryptPasswordEncoder passwordEncoder = new BCryptPasswordEncoder();

    @Autowired
    JwtTokenProvider jwtTokenProvider;

    @Autowired
    EmailService emailService;

    @Autowired
    VerificationTokenRepository verificationTokenRepository;

    

    public JwtResponse authenticateUser(LoginRequest loginRequest, HttpSession session) {
        User user = userRepository.findByUserEmail(loginRequest.getUserEmail())
                .orElseThrow(() -> new UserNotFoundException("User not found with email: " + loginRequest.getUserEmail()));

        if (!passwordEncoder.matches(loginRequest.getPassword(), user.getPassword())) { // Use passwordEncoder
            throw new RuntimeException("Invalid password!");
        }

        String jwt = jwtTokenProvider.generateJwtToken(user.getUserEmail());

        // Generate and save refresh token to session
        String refreshTokenString = jwtTokenProvider.generateRefreshToken(user.getUserEmail());
        session.setAttribute("refreshToken", refreshTokenString);

        return new JwtResponse(jwt, refreshTokenString, user.getUserId(), user.getUserEmail(), user.getUserEmail());
    }

    public JwtResponse refreshToken(String refreshTokenString, HttpSession session) {
        String storedRefreshToken = (String) session.getAttribute("refreshToken");

        if (storedRefreshToken == null || !storedRefreshToken.equals(refreshTokenString)) {
            throw new RuntimeException("Invalid or expired refresh token");
        }

        // Assuming the user information can be extracted from the refresh token or is available in the session
        // For simplicity, we'll assume the user email can be extracted from the refresh token for now.
        // In a real application, you might store user ID in the session or have a more robust way to get user.
        String userEmail = jwtTokenProvider.getUserEmailFromRefreshToken(refreshTokenString);
        User user = userRepository.findByUserEmail(userEmail)
                .orElseThrow(() -> new UserNotFoundException("User not found with email: " + userEmail));

        // Generate new access token
        String newAccessToken = jwtTokenProvider.generateJwtToken(user.getUserEmail());

        return new JwtResponse(newAccessToken, refreshTokenString, user.getUserId(), user.getUserName(), user.getUserEmail());
    }

    public void logout(HttpSession session) {
        session.removeAttribute("refreshToken");
        session.invalidate();
    }

    public boolean registerUser(SignupRequest signUpRequest) {
        if (userRepository.existsByUserName(signUpRequest.getUserName())) {
            return false; // Username is already taken!
        }

        if (userRepository.existsByUserEmail(signUpRequest.getUserEmail())) {
            return false; // Email is already in use!
        }

        // Create new user's account
        User user = new User();
        user.setUserName(signUpRequest.getUserName());
        user.setUserEmail(signUpRequest.getUserEmail());
        user.setPassword(passwordEncoder.encode(signUpRequest.getPassword())); // Use passwordEncoder
        user.setUserBirthDate(signUpRequest.getBirthDate());
        user.setUserJob(signUpRequest.getJob());
        user.setUserPhoneNumber(signUpRequest.getUserPhoneNumber());
        

        userRepository.save(user);

        // Generate verification code and send email
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
        return null; // User not found
    }

    public String findUsernameByEmail(String email) {
        Optional<User> userOptional = userRepository.findByUserEmail(email);
        return userOptional.map(User::getUserEmail).orElse(null);
    }

    @Transactional
    public void resetPassword(String email, String verificationCode, String newPassword) {
        verifyVerificationCode(email, verificationCode);

        User user = userRepository.findByUserEmail(email)
                .orElseThrow(() -> new UserNotFoundException("User not found with email: " + email));

        user.setPassword(passwordEncoder.encode(newPassword)); // Use passwordEncoder
        userRepository.save(user);
        verificationTokenRepository.deleteByEmail(email);
    }

    private String generateVerificationCode() {
        Random random = new Random();
        int code = 100000 + random.nextInt(900000); // 6-digit code
        return String.valueOf(code);
    }

    public boolean forgotPassword(String email) {
        return sendEmailVerificationCode(email, true);
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
    public boolean sendEmailVerificationCode(String email, boolean mustExist) {
        if (mustExist) {
            // 이메일이 반드시 존재해야 함 (id/pw찾기, 마이페이지)
            if (!userRepository.existsByUserEmail(email)) {
                logger.warn("Email {} does not exist. Cannot send verification code.", email);
                return false; // Email does not exist
            }
        } else {
            // 이메일이 존재하면 안 됨 (회원가입)
            if (userRepository.existsByUserEmail(email)) {
                logger.warn("Email {} already exists. Cannot send verification code.", email);
                return false; // Email already exists, do not send code
            }
        }
        try {
            String verificationCode = generateVerificationCode();
            VerificationToken existingToken = verificationTokenRepository.findByEmail(email);

            if (existingToken != null) {
                existingToken.setToken(verificationCode);
                existingToken.setExpiryDate(LocalDateTime.now().plusMinutes(15)); // Reset expiry
                verificationTokenRepository.save(existingToken);
            } else {
                VerificationToken newToken = new VerificationToken(verificationCode, email);
                verificationTokenRepository.save(newToken);
            }

            emailService.sendEmail(email, "Email Verification Code", "Your verification code is: " + verificationCode);
            return true;
        } catch (Exception e) {
            logger.error("Failed to send email verification code to {}: {}", email, e.getMessage());
            return false;
        }
    }
}