package com.example.application.entity;

import jakarta.persistence.*;
import lombok.*;

import java.time.LocalDateTime;

@Entity
@Table(name = "chat_history")
@Getter @Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class ChatHistory {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long chatId;

    private Long userId;
    private Long bookId;

    @Enumerated(EnumType.STRING)
    private Sender sender; // "AI" or "USER"

    @Column(columnDefinition = "TEXT")
    private String messageContent;

    @Enumerated(EnumType.STRING)
    private MessageType messageType;

    private LocalDateTime createdAt;

    public enum Sender {
        AI, USER
    }

    public enum MessageType {
        TEXT, SELECTION, RATING, FEEDBACK
    }
}
