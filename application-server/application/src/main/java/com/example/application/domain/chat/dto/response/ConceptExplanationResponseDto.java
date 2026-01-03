package com.example.application.domain.chat.dto.response;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

@Getter
@Builder
@AllArgsConstructor
@NoArgsConstructor
public class ConceptExplanationResponseDto {
    private String message; // 예: "Explanation generation process completed"
    private ExplanationResult result; // 예: { "explanation": "..." }

    @Getter
    @Builder
    @AllArgsConstructor
    @NoArgsConstructor
    public static class ExplanationResult {
        private String explanation;
    }
}