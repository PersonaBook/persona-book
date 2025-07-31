package com.example.application.dto.chat.response;

import com.example.application.entity.ChatHistory;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class GeneratingQuestionResponseDto {
    private Long userId;
    private Long bookId;
    @Builder.Default
    private String sender = "AI";
    private String content;
    @Builder.Default
    private String messageType = "TEXT"; // TEXT, .. (추후 확장 예정)

    private ChatHistory.ChatState chatState;

    // 🔽 추가 필드
    private String domain;         // 문제 도메인
    private String concept;        // 문제 개념
    private String problemText;    // 실제 문제 문장
    private String correctAnswer;  // 정답
}