package com.example.application.domain.auth.dto.request;

import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import lombok.Getter;
import lombok.NoArgsConstructor;

@Getter
@NoArgsConstructor
public class FindIdRequestDto {

    @NotBlank
    private String name;

    @NotBlank
    @Email
    private String email;
}