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

    @Column(columnDefinition = "TEXT")
    private String messageContent;

    @Enumerated(EnumType.STRING)
    private MessageType messageType;

    @Enumerated(EnumType.STRING)
    private Sender sender; // "AI" or "USER"

    @Enumerated(EnumType.STRING)
    private FeatureContext featureContext; // INITIAL, PROBLEM_GENERATION, PROBLEM_SOLVING, CONCEPT_EXPLANATION 등

    @Enumerated(EnumType.STRING)
    private StageContext stageContext; // START, PROMPT_NEXT_ACTION, SELECT_TYPE, ...

    private LocalDateTime createdAt;

    public enum Sender {
        AI, USER;
    }

    public enum MessageType {
        TEXT, SELECTION, RATING
    }

    // 채팅 흐름
    public enum FeatureContext {
        INITIAL,              // 초기
        PROBLEM_GENERATION,   // 예상 문제 생성
        PROBLEM_SOLVING,      // 문제 풀이
        CONCEPT_EXPLANATION   // 개념 설명
    }

    // 세부 단계
    public enum StageContext {
        START,
        PROMPT_NEXT_ACTION,
        SELECT_TYPE,
        PROMPT_CHAPTER_PAGE,
        PROMPT_CONCEPT,
        GENERATING_PROBLEM,
        PROBLEM_PRESENTED,
        USER_ANSWER,
        CORRECT_FEEDBACK,
        INCORRECT_FEEDBACK,
        EXPLANATION_PRESENTED,
        FEEDBACK_RATING,
        PROMPT_FEEDBACK_TEXT,
        INPUT_FEEDBACK_TEXT,
        RE_EXPLANATION_PRESENTED
    }
}