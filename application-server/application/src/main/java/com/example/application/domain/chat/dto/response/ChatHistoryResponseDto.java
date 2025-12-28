package com.example.application.domain.chat.dto.response;

import com.example.application.domain.chat.entity.ChatHistory;
import com.example.application.domain.chat.type.MessageType;
import com.example.application.domain.chat.type.Sender;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Getter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class ChatHistoryResponseDto {
    private Long chatId;
    private Sender sender;
    private String content;
    private MessageType messageType;
    private LocalDateTime createdAt;

    public static ChatHistoryResponseDto from(ChatHistory entity) {
        return ChatHistoryResponseDto.builder()
                .chatId(entity.getChatId())
                .sender(entity.getSender())
                .content(entity.getContent())
                .messageType(entity.getMessageType())
                .createdAt(entity.getCreatedAt())
                .build();
    }
}