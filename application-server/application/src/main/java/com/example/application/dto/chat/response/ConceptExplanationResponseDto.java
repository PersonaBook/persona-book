package com.example.application.dto.chat.response;

import lombok.*;

// 서브 클래스: result 내부 구조
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ConceptExplanationResponseDto {
    private String message;            // 예: "Explanation generation process completed"
    private ExplanationResult result; // 예: { "explanation": "..." }

    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class ExplanationResult {
        private String explanation;
    }
}