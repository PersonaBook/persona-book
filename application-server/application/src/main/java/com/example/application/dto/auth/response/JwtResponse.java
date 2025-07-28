package com.example.application.dto.auth.response;

import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
public class JwtResponse {
    private String token;
    private String refreshToken;
    private String type = "Bearer";
    private Long userId;
    private String userName;
    private String userEmail;

    public JwtResponse(String accessToken, String refreshToken, Long userId, String userName, String userEmail) {
        this.token = accessToken;
        this.refreshToken = refreshToken;
        this.userId = userId;
        this.userName = userName;
        this.userEmail = userEmail;
    }
}
