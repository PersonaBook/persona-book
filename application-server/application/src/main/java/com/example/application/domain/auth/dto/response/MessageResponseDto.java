package com.example.application.domain.auth.dto.response;

import lombok.*;
import org.springframework.http.HttpStatus;

@Getter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class MessageResponseDto {
    private int status;
    private String message;

    public MessageResponseDto(HttpStatus status, String message) {
        this.status = status.value();
        this.message = message;
    }
}
