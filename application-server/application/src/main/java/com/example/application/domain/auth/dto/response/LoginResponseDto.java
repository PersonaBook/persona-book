package com.example.application.domain.auth.dto.response;

import lombok.*;

@Getter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class LoginResponseDto {
    private String token;
    private String refreshToken;
    private String type = "Bearer";
    private Long userId;
    private String name;
    private String email;
}
