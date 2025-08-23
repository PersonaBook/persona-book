package com.example.application.service;

import com.example.application.dto.chat.AiMessageDto;
import com.example.application.dto.chat.UserMessageDto;
import com.example.application.entity.Book;
import com.example.application.entity.ChatHistory;
import com.example.application.entity.ChatHistory.ChatState;
import com.example.application.entity.User;
import com.example.application.repository.BookRepository;
import com.example.application.repository.ChatHistoryRepository;
import com.example.application.repository.UserRepository;
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
    private final UserRepository userRepository;
    private final BookRepository bookRepository;

    public void saveUserMessage(UserMessageDto dto, ChatState chatState) {
        ChatHistory history = ChatHistory.builder()
                .user(userRepository.getReferenceById(dto.getUserId())) // 프록시 객체 사용
                .book(bookRepository.getReferenceById(dto.getBookId()))  // 프록시 객체 사용
                .sender(ChatHistory.Sender.USER)
                .content(dto.getContent())
                .messageType(ChatHistory.MessageType.valueOf(dto.getMessageType()))
                .chatState(chatState)
                .createdAt(LocalDateTime.now())
                .build();

        chatHistoryRepository.save(history);
    }

    public void saveAiMessage(AiMessageDto dto, ChatState chatState) {
        ChatHistory history = ChatHistory.builder()
                .user(userRepository.getReferenceById(dto.getUserId())) // 프록시 객체 사용
                .book(bookRepository.getReferenceById(dto.getBookId()))  // 프록시 객체 사용
                .sender(ChatHistory.Sender.AI)
                .content(dto.getContent())
                .messageType(ChatHistory.MessageType.valueOf(dto.getMessageType()))
                .chatState(chatState)
                .createdAt(LocalDateTime.now())
                .build();

        chatHistoryRepository.save(history);
    }

    /**
     * 특정 사용자와 책의 전체 채팅 기록을 조회합니다.
     * @param userId 사용자 ID
     * @param bookId 책 ID
     * @return 채팅 기록 목록
     */
    public List<ChatHistory> getChatHistory(Long userId, Long bookId) {
        User user = userRepository.getReferenceById(userId);
        Book book = bookRepository.getReferenceById(bookId);
        return chatHistoryRepository.findAllByUserAndBookOrderByCreatedAtAsc(user, book);
    }

    /**
     * 특정 사용자와 책의 마지막 채팅 기록을 조회합니다.
     * @param userId 사용자 ID
     * @param bookId 책 ID
     * @return 마지막 채팅 기록
     */
    public Optional<ChatHistory> findLastMessage(Long userId, Long bookId) {
        User user = userRepository.getReferenceById(userId);
        Book book = bookRepository.getReferenceById(bookId);
        return chatHistoryRepository.findTopByUserAndBookOrderByCreatedAtDesc(user, book);
    }

    /**
     * 특정 사용자와 책의 모든 채팅 기록을 삭제합니다.
     * @param userId 사용자 ID
     * @param bookId 책 ID
     */
    public void deleteChatHistory(Long userId, Long bookId) {
        User user = userRepository.getReferenceById(userId);
        Book book = bookRepository.getReferenceById(bookId);
        chatHistoryRepository.deleteAllByUserAndBook(user, book);
    }
}