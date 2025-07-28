package com.example.application.dto.auth.request;

import jakarta.validation.constraints.NotBlank;
import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
public class LoginRequest {
    @NotBlank
    private String userEmail;

    @NotBlank
    private String password;
    
    private boolean rememberMe = false;
}
