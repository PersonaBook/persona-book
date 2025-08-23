package com.example.application.repository;

import com.example.application.entity.Book;
import com.example.application.entity.ChatHistory;
import com.example.application.entity.ChatHistory.Sender;
import com.example.application.entity.ChatHistory.ChatState;
import com.example.application.entity.User;
import jakarta.transaction.Transactional;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Modifying;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

public interface ChatHistoryRepository extends JpaRepository<ChatHistory, Long> {
    // 채팅은 특정 책과 사용자 별로 생성되고 관리 됨
    List<ChatHistory> findAllByUserAndBookOrderByCreatedAtAsc(User user, Book book);
    Optional<ChatHistory> findTopByUserAndBookOrderByCreatedAtDesc(User user, Book book);

    // (수정) User와 Book 객체를 직접 파라미터로 받도록 변경, @Modifying과 @Query를 사용하여 효율적인 삭제
    @Transactional
    @Modifying
    @Query("DELETE FROM ChatHistory ch WHERE ch.user = :user AND ch.book = :book")
    void deleteAllByUserAndBook(@Param("user") User user, @Param("book") Book book);

    Optional<ChatHistory> findTopByUserAndBookAndSenderOrderByCreatedAtDesc(User user, Book book, ChatHistory.Sender sender);
    Optional<ChatHistory> findTopByUserAndBookAndSenderAndCreatedAtAfterAndChatState(
            User user,
            Book book,
            Sender sender,
            LocalDateTime createdAt,
            ChatState chatState
    );

    // ✅ N+1 문제 해결을 위한 커스텀 쿼리 추가
    @Query("SELECT ch FROM ChatHistory ch WHERE ch.user = :user AND ch.book = :book AND ch.sender = :sender " +
            "AND ch.chatState IN (:states) ORDER BY ch.createdAt DESC")
    List<ChatHistory> findAiExplanationsWithRatingsByUserAndBookAndStates(
            @Param("user") User user,
            @Param("book") Book book,
            @Param("sender") Sender sender,
            @Param("states") List<ChatState> states
    );
}