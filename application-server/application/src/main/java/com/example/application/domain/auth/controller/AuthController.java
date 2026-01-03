package com.example.application.domain.auth.controller;

import com.example.application.domain.auth.dto.TokenDto;
import com.example.application.domain.auth.dto.request.*;
import com.example.application.domain.auth.dto.response.AuthResponseDto;
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
    public ApiResponseDto<AuthResponseDto> login(@Valid @RequestBody LoginRequestDto request) {
        return ApiResponseDto.success(authService.login(request));
    }

    @PostMapping("/register")
    public ApiResponseDto<Void> register(@Valid @RequestBody RegisterRequestDto request) {
        authService.register(request);
        return ApiResponseDto.success("회원가입이 완료되었습니다.");
    }

    @PostMapping("/token/refresh")
    public ApiResponseDto<AuthResponseDto> refreshToken(@RequestBody TokenDto tokenDto) {
        return ApiResponseDto.success(authService.refreshToken(tokenDto.getRefreshToken()));
    }

    @PostMapping("/id/find")
    public ApiResponseDto<String> findId(@Valid @RequestBody FindIdRequestDto request) {
        String email = authService.findId(request.getName(), request.getPhoneNumber());
        return ApiResponseDto.success("아이디 찾기가 완료되었습니다.", email);
    }

    @PostMapping("/password/reset")
    public ApiResponseDto<Void> resetPassword(@Valid @RequestBody PasswordResetRequestDto request) {
        authService.resetPassword(request.getName(), request.getEmail(), request.getNewPassword());
        return ApiResponseDto.success("비밀번호가 성공적으로 변경되었습니다.");
    }
}