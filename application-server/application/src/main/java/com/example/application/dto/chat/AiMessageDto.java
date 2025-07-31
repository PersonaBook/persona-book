package com.example.application.dto.chat;

import com.example.application.entity.ChatHistory.ChatState;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

// 서버 → 사용자 전송용 (AI 응답)
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class AiMessageDto {
    private Long userId;
    private Long bookId;
    @Builder.Default
    private String sender = "AI";
    private String content;
    @Builder.Default
    private String messageType = "TEXT"; // TEXT, .. (추후 확장 예정)

    private ChatState chatState;
}