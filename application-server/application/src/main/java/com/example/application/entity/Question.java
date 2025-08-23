package com.example.application.entity;

import jakarta.persistence.*;
import lombok.*;
import org.hibernate.annotations.CreationTimestamp;

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

    // 현재 엔티티에 맞춰 "question_text" 사용 (이전 "problemText" 쓰던 곳은 수정 필요)
    @Column(name = "question_text")
    private String questionText;

    @Column(name = "user_answer")
    private String userAnswer;

    @Column(name = "correct_answer")
    private String correctAnswer;

    @CreationTimestamp
    @Column(name = "created_at")
    private LocalDateTime createdAt;
}
