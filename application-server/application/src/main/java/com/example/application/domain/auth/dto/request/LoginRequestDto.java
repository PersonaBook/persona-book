package com.example.application.domain.auth.dto.request;

import jakarta.validation.constraints.NotBlank;
import lombok.*;

@Getter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class LoginRequestDto {
    @NotBlank
    private String email;

    @NotBlank
    private String password;
    
    private boolean autoLogin = false;
}
