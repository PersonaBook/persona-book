package com.example.application.global.common.dto;

import com.example.application.global.exception.ErrorCode;
import lombok.AccessLevel;
import lombok.AllArgsConstructor;
import lombok.Getter;
import org.springframework.http.HttpStatus;

@Getter
@AllArgsConstructor(access = AccessLevel.PRIVATE)
public class ApiResponseDto<T> {

    private final boolean success;
    private final String code;  // "200", "404" 등(추후 확장 가능성을 고려해, String 타입으로 지정)
    private final String message;
    private final T data;

    // 성공 Factory Methods
    public static <T> ApiResponseDto<T> success() {
        return new ApiResponseDto<>(
                true,
                String.valueOf(HttpStatus.OK.value()),
                HttpStatus.OK.getReasonPhrase(),
                null
        );
    }

    public static <T> ApiResponseDto<T> success(String message) {
        return new ApiResponseDto<>(
                true,
                String.valueOf(HttpStatus.OK.value()),
                message,
                null
        );
    }

    public static <T> ApiResponseDto<T> success(T data) {
        return new ApiResponseDto<>(
                true,
                String.valueOf(HttpStatus.OK.value()),
                HttpStatus.OK.getReasonPhrase(),
                data
        );
    }

    public static <T> ApiResponseDto<T> success(String message, T data) {
        return new ApiResponseDto<>(
                true,
                String.valueOf(HttpStatus.OK.value()),
                message,
                data
        );
    }


    // 실패 Factory Methods
    public static <T> ApiResponseDto<T> fail(ErrorCode errorCode) {
        return new ApiResponseDto<>(
                false,
                String.valueOf(errorCode.getHttpStatus().value()),
                errorCode.getMessage(),
                null
        );
    }

    public static <T> ApiResponseDto<T> fail(String message) {
        return new ApiResponseDto<>(false, "400", message, null);
    }
}