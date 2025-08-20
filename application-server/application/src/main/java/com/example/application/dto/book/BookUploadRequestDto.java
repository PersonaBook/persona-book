package com.example.application.dto.book;

import com.fasterxml.jackson.annotation.JsonProperty;
import jakarta.validation.constraints.NotBlank;

public record BookUploadRequestDto(
        @NotBlank String title,
        @JsonProperty("file_base64") @NotBlank String fileBase64
) { }