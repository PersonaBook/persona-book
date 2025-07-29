package com.example.application.entity;

import jakarta.persistence.*;
import lombok.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "question")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Question {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "answer_id")
    private Long id;

    @Column(name = "user_id", nullable = false)
    private Long userId;

    @Column(name = "book_id", nullable = false)
    private Long bookId;

    @Column(name = "chat_id", nullable = false)
    private Long chatId;

    @Column(name = "start_page")
    private Integer startPage;

    @Column(name = "end_page")
    private Integer endPage;

    @Column(name = "concept_keyword")
    private String conceptKeyword;

    @Column(name = "is_concept_explained")
    private Boolean isConceptExplained;

    @Column(name = "created_at")
    private LocalDateTime createdAt;

    @Column(name = "cor_answer")
    private String correctAnswer;
}
