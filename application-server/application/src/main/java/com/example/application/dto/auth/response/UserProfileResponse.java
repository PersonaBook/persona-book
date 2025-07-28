package com.example.application.dto.auth.response;

import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.Setter;

import java.time.LocalDate;

@Getter
@Setter
@AllArgsConstructor
public class UserProfileResponse {
    private Long userId;
    private String userName;
    private String userEmail;
    private LocalDate birthDate;
    private String job;
    // Add other user details as needed
}
