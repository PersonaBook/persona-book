package com.example.application.dto.auth.response;

import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.Setter;

import java.time.LocalDate;

@Getter
@Setter
@AllArgsConstructor
public class UserProfileResponseDto {
    private Long userId;
    private String name;
    private String email;
    private LocalDate birthDate;
    private String job;
}
