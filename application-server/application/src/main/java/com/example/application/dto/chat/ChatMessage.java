package com.example.application.dto.chat;

import lombok.Data;

@Data
public class ChatMessage {
    private String senderId;
    private String content;
    private String timestamp;
}
