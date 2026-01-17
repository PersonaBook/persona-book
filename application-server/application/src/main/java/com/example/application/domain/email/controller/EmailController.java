package com.example.application.domain.email.controller;

import com.example.application.domain.email.dto.EmailRequestDto;
import com.example.application.domain.email.dto.EmailVerifyRequestDto;
import com.example.application.domain.email.service.EmailService;
import com.example.application.global.common.dto.ApiResponseDto;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/email")
@RequiredArgsConstructor
public class EmailController {

    private final EmailService emailService;

    @PostMapping("/send/code")
    public ApiResponseDto<Void> sendVerificationCode(@Valid @RequestBody EmailRequestDto request) {
        emailService.sendVerificationCode(request.getEmail());
        return ApiResponseDto.success("인증번호가 발송되었습니다.");
    }

    @PostMapping("/verification")
    public ApiResponseDto<Void> verifyCode(@Valid @RequestBody EmailVerifyRequestDto request) {
        emailService.verifyCode(request.getEmail(), request.getCode());
        return ApiResponseDto.success("이메일 인증에 성공했습니다.");
    }
}