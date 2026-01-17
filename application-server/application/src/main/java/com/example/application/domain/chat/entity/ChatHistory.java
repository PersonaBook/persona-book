package com.example.application.domain.chat.entity;

import com.example.application.domain.book.entity.Book;
import com.example.application.domain.user.entity.User;
import com.example.application.domain.chat.type.ChatState;
import com.example.application.domain.chat.type.MessageType;
import com.example.application.domain.chat.type.Sender;
import com.example.application.global.common.entity.BaseTimeEntity;
import jakarta.persistence.*;
import lombok.*;

@Entity
@Table(name = "chat_history")
@Getter @Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class ChatHistory extends BaseTimeEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "chat_id")
    private Long chatId;

    // ─────────────── 연관관계 (단방향) ───────────────
    // ✅ 기존 Long userId/bookId → 연관관계로 교체
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_id", nullable = false)
    private User user;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "book_id", nullable = false)
    private Book book;

    @Column(columnDefinition = "TEXT")
    private String content;

    @Enumerated(EnumType.STRING)
    @Column(name = "message_type")
    private MessageType messageType;

    @Enumerated(EnumType.STRING)
    @Column(name = "sender")
    private Sender sender; // "AI" or "USER"

    @Enumerated(EnumType.STRING)
    @Column(name = "chat_state")
    private ChatState chatState;

}