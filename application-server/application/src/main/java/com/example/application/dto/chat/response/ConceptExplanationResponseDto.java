package com.example.application.dto.chat.response;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;

@Getter
@Builder
@AllArgsConstructor
public class ConceptExplanationResponseDto {
    private String message; // 예: "Explanation generation process completed"
    private ExplanationResult result; // 예: { "explanation": "..." }

    @Getter
    @Builder
    @AllArgsConstructor
    public static class ExplanationResult {
        private String explanation;
    }
}