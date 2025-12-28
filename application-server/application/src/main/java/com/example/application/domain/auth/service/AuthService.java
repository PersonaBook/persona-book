package com.example.application.domain.auth.service;

import com.example.application.domain.auth.dto.TokenDto;
import com.example.application.domain.auth.dto.request.LoginRequestDto;
import com.example.application.domain.auth.dto.request.RegisterRequestDto;
import com.example.application.domain.auth.dto.response.AuthResponseDto;
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

@Service
@Slf4j
@RequiredArgsConstructor
@Transactional(readOnly = true)
public class AuthService {

    private final PasswordEncoder passwordEncoder;
    private final UserRepository userRepository;
    private final JwtProvider jwtProvider;

    @Transactional
    public AuthResponseDto login(LoginRequestDto request) {
        User user = userRepository.findByEmail(request.getEmail())
                .orElseThrow(() -> new CustomException(ErrorCode.USER_NOT_FOUND));

        if (!passwordEncoder.matches(request.getPassword(), user.getPassword())) {
            throw new CustomException(ErrorCode.INVALID_PASSWORD);
        }

        return issueTokens(user);
    }

    public AuthResponseDto refreshToken(String refreshToken) {
        if (refreshToken == null || !jwtProvider.isValidToken(refreshToken)) {
            throw new CustomException(ErrorCode.INVALID_TOKEN);
        }

        Long userId = jwtProvider.getUserId(refreshToken);
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new CustomException(ErrorCode.USER_NOT_FOUND));

        return issueTokens(user);
    }

    private AuthResponseDto issueTokens(User user) {
        TokenDto tokenDto = TokenDto.builder()
                .accessToken(jwtProvider.createAccessToken(user.getUserId(), user.getEmail()))
                .refreshToken(jwtProvider.createRefreshToken(user.getUserId(), user.getEmail()))
                .build();

        return AuthResponseDto.builder()
                .userId(user.getUserId())
                .name(user.getName())
                .email(user.getEmail())
                .token(tokenDto)
                .build();
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
    }

    public String findId(String name, String phoneNumber) {
        User user = userRepository.findByNameAndPhoneNumber(name, phoneNumber)
                .orElseThrow(() -> new CustomException(ErrorCode.USER_NOT_FOUND));

        return user.getEmail();
    }

    @Transactional
    public void resetPassword(String name, String email, String newPassword) {
        User user = userRepository.findByNameAndEmail(name, email)
                .orElseThrow(() -> new CustomException(ErrorCode.USER_NOT_FOUND));

        user.resetPassword(passwordEncoder.encode(newPassword));
    }
}