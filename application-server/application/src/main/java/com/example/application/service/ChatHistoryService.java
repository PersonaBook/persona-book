package com.example.application.service;

import com.example.application.dto.chat.AiMessageDto;
import com.example.application.dto.chat.UserMessageDto;
import com.example.application.entity.ChatHistory;
import com.example.application.entity.ChatHistory.MessageType;
import com.example.application.entity.ChatHistory.Sender;
import com.example.application.repository.ChatHistoryRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.List;

@Service
@RequiredArgsConstructor
public class ChatHistoryService {

    private final ChatHistoryRepository chatHistoryRepository;

    public void saveUserMessage(UserMessageDto dto, Long bookId) {
        ChatHistory history = ChatHistory.builder()
                .userId(Long.parseLong(dto.getSenderId()))
                .bookId(bookId)
                .sender(Sender.USER)
                .messageContent(dto.getContent())
                .messageType(MessageType.valueOf(dto.getMessageType().toUpperCase()))
                .createdAt(LocalDateTime.now())
                .build();
        chatHistoryRepository.save(history);
    }

    public void saveAiMessage(AiMessageDto dto, Long userId, Long bookId) {
        ChatHistory history = ChatHistory.builder()
                .userId(userId)
                .bookId(bookId)
                .sender(Sender.AI)
                .messageContent(dto.getContent())
                .messageType(MessageType.valueOf(dto.getMessageType().toUpperCase()))
                .createdAt(LocalDateTime.now())
                .build();
        chatHistoryRepository.save(history);
    }

    public List<ChatHistory> getChatHistory(Long userId, Long bookId) {
        return chatHistoryRepository.findAllByUserIdAndBookIdOrderByCreatedAtAsc(userId, bookId);
    }
}