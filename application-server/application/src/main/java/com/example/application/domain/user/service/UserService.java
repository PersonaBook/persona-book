package com.example.application.domain.user.service;

import com.example.application.domain.user.dto.request.UserProfileUpdateRequestDto;
import com.example.application.domain.user.dto.response.UserProfileResponseDto;
import com.example.application.domain.user.entity.User;
import com.example.application.domain.user.repositroy.UserRepository;
import com.example.application.global.exception.CustomException;
import com.example.application.global.exception.ErrorCode;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
public class UserService {

    private final UserRepository userRepository;

    @Transactional(readOnly = true)
    public UserProfileResponseDto getUserProfile(Long userId) {
        User user = findUserById(userId);
        return UserProfileResponseDto.from(user);
    }

    @Transactional
    public void updateProfile(Long userId, UserProfileUpdateRequestDto request) {
        User user = findUserById(userId);
        user.updateProfile(request);
    }

    private User findUserById(Long userId) {
        return userRepository.findById(userId)
                .orElseThrow(() -> new CustomException(ErrorCode.USER_NOT_FOUND));
    }
}