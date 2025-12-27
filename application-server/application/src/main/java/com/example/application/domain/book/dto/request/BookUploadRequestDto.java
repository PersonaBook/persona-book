package com.example.application.domain.book.dto.request;

import com.fasterxml.jackson.annotation.JsonProperty;
import jakarta.validation.constraints.NotBlank;
import lombok.*;

@Getter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class BookUploadRequestDto {
    @NotBlank
    private String title;

    @NotBlank
    @JsonProperty("file_base64")
    private String fileBase64;
}
