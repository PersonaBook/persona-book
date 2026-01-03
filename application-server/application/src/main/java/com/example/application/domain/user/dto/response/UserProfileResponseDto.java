package com.example.application.domain.user.dto.response;

import com.example.application.domain.user.entity.User;
import lombok.*;

import java.time.LocalDate;

@Getter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class UserProfileResponseDto {
    private Long userId;
    private String name;
    private String email;
    private String phoneNumber;
    private LocalDate birthDate;
    private String job;

    public static UserProfileResponseDto from(User user) {
        return UserProfileResponseDto.builder()
                .userId(user.getUserId())
                .name(user.getName())
                .email(user.getEmail())
                .phoneNumber(user.getPhoneNumber())
                .birthDate(user.getBirthDate())
                .job(user.getJob())
                .build();
    }
}
