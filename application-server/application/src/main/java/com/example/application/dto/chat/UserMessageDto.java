package com.example.application.dto.chat;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

// 사용자 → 서버 전송용
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class UserMessageDto {
    private String senderId;
    private String receiverId;
    private Long bookId;
    private String content;
    private String timestamp;
    private String messageType; // text, selection, rating 등
}