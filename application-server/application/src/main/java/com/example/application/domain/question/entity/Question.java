package com.example.application.domain.question.entity;

import com.example.application.domain.book.entity.Book;
import com.example.application.domain.user.entity.User;
import jakarta.persistence.*;
import lombok.*;

import java.time.LocalDateTime;

@Getter @Setter
@NoArgsConstructor @AllArgsConstructor
@Builder
@Entity
@Table(name = "question")
public class Question {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "question_id")
    private Long questionId;

    // ─────────────── 연관관계 (단방향) ───────────────
    // ✅ 기존 Long userId/bookId → 연관관계로 교체
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_id", nullable = false)
    private User user;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "book_id", nullable = false)
    private Book book;

    @Column(name = "domain")
    private String domain;

    @Column(name = "concept")
    private String concept;

    @Column(name = "text")
    private String text;

    @Column(name = "user_answer")
    private String userAnswer;

    @Column(name = "correct_answer")
    private String correctAnswer;

    @Column(name = "created_at")
    private LocalDateTime createdAt;

    @Column(name = "updated_at")
    private LocalDateTime updatedAt;

    // ─────────────── 라이프사이클 메서드 ───────────────
    @PrePersist
    protected void onCreate() {
        this.createdAt = LocalDateTime.now();
    }

    @PreUpdate
    protected void onUpdate() {
        this.updatedAt = LocalDateTime.now();
    }
}
