package com.example.application.domain.user.controller;

import com.example.application.domain.user.dto.request.UserProfileUpdateRequestDto;
import com.example.application.domain.user.dto.response.UserProfileResponseDto;
import com.example.application.domain.user.service.UserService;
import com.example.application.global.dto.ApiResponseDto;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/user")
@RequiredArgsConstructor
public class UserController {

    private final UserService userService;

    @GetMapping("/profile")
    public ApiResponseDto<UserProfileResponseDto> getProfile(
            @RequestAttribute("userId") Long userId
    ) {
        return ApiResponseDto.success(userService.getUserProfile(userId));
    }

    @PatchMapping("/profile")
    public ApiResponseDto<Void> updateProfile(
            @RequestAttribute("userId") Long userId,
            @Valid @RequestBody UserProfileUpdateRequestDto request
    ) {
        userService.updateProfile(userId, request);
        return ApiResponseDto.success("회원정보가 성공적으로 수정되었습니다.");
    }
}