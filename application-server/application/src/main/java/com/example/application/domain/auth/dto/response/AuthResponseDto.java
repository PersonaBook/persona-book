package com.example.application.domain.auth.dto.response;

import com.example.application.domain.auth.dto.TokenDto;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

@Getter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class AuthResponseDto {
    private Long userId;
    private String name;
    private String email;

    private TokenDto token;
}