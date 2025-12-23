package com.example.application.dto.auth.response;

import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.Setter;
import org.springframework.http.HttpStatus;

@Getter
@Setter
public class MessageResponseDto {
    private int status;
    private String message;

    public MessageResponseDto(HttpStatus status, String message) {
        this.status = status.value();
        this.message = message;
    }
}
