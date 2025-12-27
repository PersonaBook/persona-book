package com.example.application.domain.auth.dto.response;

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
    private LocalDate birthDate;
    private String job;
}
