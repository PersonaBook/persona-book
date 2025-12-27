package com.example.application.global.dto;

import com.example.application.global.exception.ErrorCode;
import lombok.AccessLevel;
import lombok.AllArgsConstructor;
import lombok.Getter;

@Getter
@AllArgsConstructor(access = AccessLevel.PRIVATE)
public class ApiResponseDto<T> {

    private static final String DEFAULT_SUCCESS_MESSAGE = "요청이 성공적으로 처리되었습니다.";

    private final boolean success;
    private final String message;
    private final T data;

    // ────────────────────────────
    // 성공
    // ────────────────────────────
    public static <T> ApiResponseDto<T> success() {
        return new ApiResponseDto<>(true, DEFAULT_SUCCESS_MESSAGE, null);
    }

    public static <T> ApiResponseDto<T> success(String message) {
        return new ApiResponseDto<>(true, message, null);
    }

    public static <T> ApiResponseDto<T> success(T data) {
        return new ApiResponseDto<>(true, DEFAULT_SUCCESS_MESSAGE, data);
    }

    public static <T> ApiResponseDto<T> success(String message, T data) {
        return new ApiResponseDto<>(true, message, data);
    }

    // ────────────────────────────
    // 실패
    // ────────────────────────────
    public static <T> ApiResponseDto<T> fail(ErrorCode errorCode) {
        return new ApiResponseDto<>(false, errorCode.getMessage(), null);
    }

    public static <T> ApiResponseDto<T> fail(String message) {
        return new ApiResponseDto<>(false, message, null);
    }
}