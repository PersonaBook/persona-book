package com.example.application.dto.auth.response;

import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
public class LoginResponseDto {
    private String token;
    private String refreshToken;
    private String type = "Bearer";
    private Long userId;
    private String name;
    private String email;

    public LoginResponseDto(String accessToken, String refreshToken, Long userId, String name, String email) {
        this.token = accessToken;
        this.refreshToken = refreshToken;
        this.userId = userId;
        this.name = name;
        this.email = email;
    }
}
