package com.example.application.domain.user.service;

import com.example.application.dto.user.request.UserUpdateRequestDto;
import com.example.application.domain.auth.dto.response.UserProfileResponseDto;
import com.example.application.domain.user.entity.User;
import com.example.application.domain.user.repositroy.UserRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
public class UserService {

    private final UserRepository userRepository;

    @Transactional
    public void updateProfile(User user, UserUpdateRequestDto request) {
        // 엔티티에게 "수정해줘" 라고 요청 (Rich Domain Model)
        user.updateProfile(
                request.getName(),
                request.getEmail(),
                request.getPhoneNumber(),
                request.getBirthDate(),
                request.getJob(),
                request.getOtherUserJob()
        );
        // Dirty Checking으로 인해 save() 호출 불필요 (Transactional 종료 시 자동 업데이트)
    }

    @Transactional(readOnly = true)
    public UserProfileResponseDto getUserProfile(Long userId) {
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new IllegalArgumentException("사용자를 찾을 수 없습니다."));
        return UserProfileResponseDto.from(user);
    }
}