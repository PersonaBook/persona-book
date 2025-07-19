package com.example.application.dto.chat;

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
    @Builder.Default
    private String senderId = "AI";
    private String receiverId;
    private Long bookId;
    private String content;
    private String timestamp;
    private String messageType; // text, feedback 등

    // 추가 필드 예시
    // private String source; // langchain, api, vectorDB 등
    // private List<String> references;
    // private Boolean requiresFollowup;
}