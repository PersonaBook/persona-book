package com.example.application.domain.chat.service;

import com.example.application.domain.chat.dto.AiMessageDto;
import com.example.application.domain.chat.dto.UserMessageDto;
import com.example.application.domain.book.entity.Book;
import com.example.application.domain.chat.dto.response.ChatHistoryResponseDto;
import com.example.application.domain.chat.entity.ChatHistory;
import com.example.application.domain.chat.type.ChatState;
import com.example.application.domain.user.entity.User;
import com.example.application.domain.book.repository.BookRepository;
import com.example.application.domain.chat.repository.ChatHistoryRepository;
import com.example.application.domain.user.repositroy.UserRepository;
import com.example.application.domain.chat.type.Sender;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

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
                .sender(Sender.USER)
                .content(dto.getContent())
                .messageType(dto.getMessageType())
                .chatState(chatState)
                .createdAt(LocalDateTime.now())
                .build();

        chatHistoryRepository.save(history);
    }

    public void saveAiMessage(AiMessageDto dto, ChatState chatState) {
        ChatHistory history = ChatHistory.builder()
                .user(userRepository.getReferenceById(dto.getUserId())) // 프록시 객체 사용
                .book(bookRepository.getReferenceById(dto.getBookId()))  // 프록시 객체 사용
                .sender(Sender.AI)
                .content(dto.getContent())
                .messageType(dto.getMessageType())
                .chatState(chatState)
                .createdAt(LocalDateTime.now())
                .build();

        chatHistoryRepository.save(history);
    }

    @Transactional(readOnly = true)
    public List<ChatHistoryResponseDto> getChatHistory(Long userId, Long bookId) {
        User user = userRepository.getReferenceById(userId);
        Book book = bookRepository.getReferenceById(bookId);

        List<ChatHistory> histories = chatHistoryRepository.findAllByUserAndBookOrderByCreatedAtAsc(user, book);

        return histories.stream()
                .map(ChatHistoryResponseDto::from)
                .toList();
    }

    @Transactional(readOnly = true)
    public Optional<ChatHistoryResponseDto> findLastMessage(Long userId, Long bookId) {
        User user = userRepository.getReferenceById(userId);
        Book book = bookRepository.getReferenceById(bookId);

        return chatHistoryRepository.findTopByUserAndBookOrderByCreatedAtDesc(user, book)
                .map(ChatHistoryResponseDto::from);
    }

    public void deleteChatHistory(Long userId, Long bookId) {
        User user = userRepository.getReferenceById(userId);
        Book book = bookRepository.getReferenceById(bookId);
        chatHistoryRepository.deleteAllByUserAndBook(user, book);
    }
}