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
    private String content;

    @Enumerated(EnumType.STRING)
    private MessageType messageType;

    @Enumerated(EnumType.STRING)
    private Sender sender; // "AI" or "USER"

    @Enumerated(EnumType.STRING)
    private ChatState chatState; // ✅ 단일 상태 (기존 feature/stage 통합)

    private LocalDateTime createdAt;

    public enum Sender {
        AI, USER;
    }

    public enum MessageType {
        TEXT, SELECTION, RATING
    }

    public enum ChatState {

        // ────────────────────────────────
        // 0. 기능 선택 진입
        // ────────────────────────────────
        WAITING_USER_SELECT_FEATURE,         // 기능 선택: 1. 예상 문제 생성 / 2. 페이지 찾기 / 3. 개념 설명

        // ────────────────────────────────
        // 1. 예상 문제 생성 흐름
        // ────────────────────────────────
        WAITING_PROBLEM_CRITERIA_SELECTION,  // 문제 기준 선택 (1. 챕터/페이지, 2. 개념)
        WAITING_PROBLEM_CONTEXT_INPUT,       // 챕터/페이지 번호 또는 개념 키워드 입력
        GENERATING_QUESTION_WITH_RAG,        // ✅ FastAPI 호출로 문제 생성
        WAITING_USER_ANSWER,                 // 사용자 답 입력 대기
        GENERATING_ADDITIONAL_QUESTION_WITH_RAG, // ✅ FastAPI 호출로 문제 생성
        EVALUATING_ANSWER_AND_LOGGING,       // ✅ FastAPI 호출 → 정오답 판단 및 오답 저장

        WAITING_NEXT_ACTION_AFTER_LEARNING,  // 다음 액션: 1. 다음 문제 / 2. 기능 선택
        PRESENTING_CONCEPT_EXPLANATION,      // ✅ 오답 개념 설명 (FastAPI 호출)
        WAITING_CONCEPT_RATING,              // 사용자 설명 평가 점수 입력
        WAITING_REASON_FOR_LOW_RATING,       // 낮은 점수(1~3점) 입력 시 사유 요청
        REEXPLAINING_CONCEPT,                // ✅ 보충 설명 요청 (FastAPI 호출 후 반복 평가)

        // ────────────────────────────────
        // 2. 개념 설명 흐름
        // ────────────────────────────────
        WAITING_CONCEPT_INPUT,               // 설명 받고 싶은 개념 입력
        // 이후 흐름은 동일:
        // → PRESENTING_CONCEPT_EXPLANATION → WAITING_CONCEPT_RATING → (반복)

        // ────────────────────────────────
        // 3. 페이지 찾기 흐름
        // ────────────────────────────────
        WAITING_KEYWORD_FOR_PAGE_SEARCH,     // 사용자 키워드 입력 대기
        PROCESSING_PAGE_SEARCH_RESULT        // ✅ FastAPI 호출 → 키워드 기반 관련 페이지/챕터 제공
        // 이후 → WAITING_USER_SELECT_FEATURE로 루프
    }
}