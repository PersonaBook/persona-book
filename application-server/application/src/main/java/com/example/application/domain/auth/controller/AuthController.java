package com.example.application.domain.auth.controller;

import com.example.application.domain.auth.dto.request.*;
import com.example.application.domain.auth.dto.response.LoginResponseDto;
import com.example.application.domain.auth.service.AuthService;
import com.example.application.global.dto.ApiResponseDto;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/auth")
@RequiredArgsConstructor
public class AuthController {

    private final AuthService authService;

    @PostMapping("/login")
    public ApiResponseDto<LoginResponseDto> login(@Valid @RequestBody LoginRequestDto request) {
        return ApiResponseDto.success(authService.login(request));
    }

    @PostMapping("/register")
    public ApiResponseDto<String> register(@Valid @RequestBody RegisterRequestDto request) {
        authService.register(request);
        return ApiResponseDto.success("회원가입이 완료되었습니다. 이메일 인증을 확인해주세요.");
    }

    @PostMapping("/token/refresh")
    public ApiResponseDto<LoginResponseDto> refreshToken(@Valid @RequestBody RefreshTokenRequestDto request) {
        return ApiResponseDto.success(authService.refreshToken(request.getRefreshToken()));
    }

    @PostMapping("/logout")
    public ApiResponseDto<String> logout(@RequestBody RefreshTokenRequestDto request) {
        authService.logout(request.getRefreshToken());
        return ApiResponseDto.success("로그아웃 되었습니다.");
    }

    @PostMapping("/email/verify")
    public ApiResponseDto<String> verifyEmail(@Valid @RequestBody EmailVerifyRequestDto request) {
        authService.verifyEmail(request.getEmail(), request.getCode());
        return ApiResponseDto.success("이메일 인증에 성공했습니다.");
    }

    @PostMapping("/email/send")
    public ApiResponseDto<String> sendEmail(@Valid @RequestBody EmailSendRequestDto request) {
        boolean mustExist = "findId".equals(request.getType()) || "findPassword".equals(request.getType());

        authService.requestVerificationCode(request.getEmail(), mustExist);
        return ApiResponseDto.success("인증번호를 발송했습니다.");
    }

    @PostMapping("/id/find")
    public ApiResponseDto<String> findId(@Valid @RequestBody FindIdRequestDto request) {
        String username = authService.findId(request.getName(), request.getEmail());
        return ApiResponseDto.success("귀하의 아이디는: " + username);
    }

    @PostMapping("/password/reset")
    public ApiResponseDto<String> resetPassword(@Valid @RequestBody PasswordResetRequestDto request) {
        authService.resetPassword(request.getName(), request.getEmail(), request.getNewPassword());
        return ApiResponseDto.success("비밀번호가 성공적으로 변경되었습니다.");
    }
}