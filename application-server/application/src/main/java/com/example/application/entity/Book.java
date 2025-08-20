package com.example.application.entity;

import jakarta.persistence.*;
import lombok.*;
import java.time.LocalDateTime;
import java.util.HashSet;
import java.util.Set;

@Getter @Setter
@NoArgsConstructor @AllArgsConstructor
@Builder
@Entity
@Table(name = "book")
public class Book {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "book_id")
    private Long bookId;

    // ✅ 기존 Long userId → 연관관계로 교체
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_id", nullable = false)  // FK 컬럼 유지
    private User user;

    @Column(name = "title")
    private String title;

    @Column(name = "file_base64", columnDefinition = "LONGTEXT")
    private String fileBase64;

    @Column(name = "created_at")
    private LocalDateTime createdAt;

    @Column(name = "deleted_at")
    private LocalDateTime deletedAt;

    @Column(name = "last_accessed_at")
    private LocalDateTime lastAccessedAt;

    // 임베딩 상태 관련 필드
    @Column(name = "embedding_status")
    private String embeddingStatus;

    @Column(name = "embedding_completed_at")
    private LocalDateTime embeddingCompletedAt;

    // ─────────────── 연관관계 (역방향) ───────────────
    @Builder.Default
    @OneToMany(mappedBy = "book", fetch = FetchType.LAZY)
    private Set<Question> questions = new HashSet<>();

    @Builder.Default
    @OneToMany(mappedBy = "book", fetch = FetchType.LAZY)
    private Set<ChatHistory> chatHistories = new HashSet<>();

    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
        lastAccessedAt = LocalDateTime.now();
    }

    @PreUpdate
    protected void onUpdate() {
        lastAccessedAt = LocalDateTime.now();
    }
}
