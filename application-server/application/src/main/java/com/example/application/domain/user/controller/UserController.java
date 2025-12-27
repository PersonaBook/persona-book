package com.example.application.domain.user.controller;

import com.example.application.domain.user.dto.requeset.UserProfileUpdateRequestDto;
import com.example.application.domain.user.dto.response.UserProfileResponseDto;
import com.example.application.domain.user.service.UserService;
import com.example.application.global.dto.ApiResponseDto; // ✅ 글로벌 DTO 사용
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

    @GetMapping("/{userId}")
    public ApiResponseDto<UserProfileResponseDto> getUserById(@PathVariable Long userId) {
        return ApiResponseDto.success(userService.getUserProfile(userId));
    }

    @PatchMapping("/profile")
    public ApiResponseDto<String> updateProfile(
            @RequestAttribute("userId") Long userId,
            @RequestBody UserProfileUpdateRequestDto request
    ) {
        userService.updateProfile(userId, request);
        return ApiResponseDto.success("회원정보가 성공적으로 수정되었습니다.");
    }
}