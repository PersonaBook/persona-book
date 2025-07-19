package com.example.application.repository;

import com.example.application.entity.ChatHistory;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface ChatHistoryRepository extends JpaRepository<ChatHistory, Long> {
    // 채팅은 특정 책과 사용자 별로 생성되고 관리 됨
    List<ChatHistory> findAllByUserIdAndBookIdOrderByCreatedAtAsc(Long userId, Long bookId);
}