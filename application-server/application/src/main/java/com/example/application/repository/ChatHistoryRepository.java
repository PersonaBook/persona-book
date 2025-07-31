package com.example.application.repository;

import com.example.application.entity.ChatHistory;
import org.springframework.data.jpa.repository.JpaRepository;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

public interface ChatHistoryRepository extends JpaRepository<ChatHistory, Long> {
    // 채팅은 특정 책과 사용자 별로 생성되고 관리 됨
    List<ChatHistory> findAllByUserIdAndBookIdOrderByCreatedAtAsc(Long userId, Long bookId);
    Optional<ChatHistory> findTopByUserIdAndBookIdOrderByCreatedAtDesc(Long userId, Long bookId);
    void deleteAllByUserIdAndBookId(Long userId, Long bookId);

    List<ChatHistory> findByUserIdAndBookIdAndSenderAndChatState(Long userId, Long bookId, ChatHistory.Sender sender, ChatHistory.ChatState chatState);
    Optional<ChatHistory> findTopByUserIdAndBookIdAndSenderOrderByCreatedAtDesc(Long userId, Long bookId, ChatHistory.Sender sender);
    Optional<ChatHistory> findTopByUserIdAndBookIdAndSenderAndCreatedAtAfterAndChatState(
            Long userId,
            Long bookId,
            ChatHistory.Sender sender,
            LocalDateTime createdAt,
            ChatHistory.ChatState chatState
    );
}