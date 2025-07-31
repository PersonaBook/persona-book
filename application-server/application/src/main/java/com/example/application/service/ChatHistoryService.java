package com.example.application.service;

import com.example.application.dto.chat.AiMessageDto;
import com.example.application.dto.chat.UserMessageDto;
import com.example.application.entity.ChatHistory;
import com.example.application.entity.ChatHistory.ChatState;
import com.example.application.entity.ChatHistory.MessageType;
import com.example.application.entity.ChatHistory.Sender;
import com.example.application.repository.ChatHistoryRepository;
import jakarta.transaction.Transactional;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

@Service
@RequiredArgsConstructor
@Transactional
public class ChatHistoryService {

    private final ChatHistoryRepository chatHistoryRepository;

    public void saveUserMessage(UserMessageDto dto, ChatState chatState) {
        ChatHistory history = ChatHistory.builder()
                .userId(dto.getUserId())
                .bookId(dto.getBookId())
                .sender(ChatHistory.Sender.USER)
                .content(dto.getContent())
                .messageType(ChatHistory.MessageType.valueOf(dto.getMessageType()))
                .chatState(chatState)
//                .ratingScore(dto.getRatingScore())
//                .associatedConcept(dto.getAssociatedConcept())
                .createdAt(LocalDateTime.now())
                .build();

        chatHistoryRepository.save(history);
    }

    public void saveAiMessage(AiMessageDto dto, ChatState chatState) {
        ChatHistory history = ChatHistory.builder()
                .userId(dto.getUserId())
                .bookId(dto.getBookId())
                .sender(ChatHistory.Sender.AI)
                .content(dto.getContent())
                .messageType(ChatHistory.MessageType.valueOf(dto.getMessageType()))
                .chatState(chatState)
                .createdAt(LocalDateTime.now())
                .build();

        chatHistoryRepository.save(history);
    }

    public List<ChatHistory> getChatHistory(Long userId, Long bookId) {
        return chatHistoryRepository.findAllByUserIdAndBookIdOrderByCreatedAtAsc(userId, bookId);
    }

    public Optional<ChatHistory> findLastMessage(Long userId, Long bookId) {
        return chatHistoryRepository.findTopByUserIdAndBookIdOrderByCreatedAtDesc(userId, bookId);
    }

    public void deleteChatHistory(Long userId, Long bookId) {
        chatHistoryRepository.deleteAllByUserIdAndBookId(userId, bookId);
    }
}