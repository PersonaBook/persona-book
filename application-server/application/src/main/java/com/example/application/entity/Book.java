package com.example.application.entity;

import com.example.application.type.EmbeddingState;
import jakarta.persistence.*;
import lombok.*;
import java.time.LocalDateTime;

@Getter
@NoArgsConstructor
@AllArgsConstructor
@Builder
@Entity
@Table(name = "book")
public class Book {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "book_id")
    private Long bookId;

    // ─────────────── 연관관계 (단방향) ───────────────
    // ✅ 기존 Long userId → 연관관계로 교체
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_id", nullable = false)
    private User user;

    @Column(name = "title", nullable = false)
    private String title;

    @Column(name = "file_base64", columnDefinition = "LONGTEXT")
    private String fileBase64;

    @Column(name = "created_at", updatable = false)
    private LocalDateTime createdAt;

    @Column(name = "updated_at")
    private LocalDateTime updatedAt;

    @Column(name = "embedding_completed_at")
    private LocalDateTime embeddingCompletedAt;

    @Enumerated(EnumType.STRING)
    @Column(name = "embedding_state", nullable = false)
    private EmbeddingState embeddingState;


    // ─────────────── 라이프사이클 메서드 (자동 실행) ───────────────
    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
        updatedAt = LocalDateTime.now();

        if (embeddingState == null) {
            embeddingState = EmbeddingState.PENDING;
        }
    }

    @PreUpdate
    protected void onUpdate() {
        updatedAt = LocalDateTime.now();
    }


    // ─────────────── 비즈니스 메서드 (Setter 대체) ───────────────
    public void updateEmbeddingState(EmbeddingState state) {
        this.embeddingState = state;
        if (state == EmbeddingState.COMPLETED) {
            this.embeddingCompletedAt = LocalDateTime.now();
        }
    }


    // ─────────────── 연관관계 (역방향) ───────────────
    // 역방향 매핑은 필요한 경우에만 사용
    // 데이터가 많아질 경우, 성능 저하
    // @Builder.Default
    // @OneToMany(mappedBy = "book", fetch = FetchType.LAZY)
    // private Set<Question> questions = new HashSet<>();
    //
    // @Builder.Default
    // @OneToMany(mappedBy = "book", fetch = FetchType.LAZY)
    // private Set<ChatHistory> chatHistories = new HashSet<>();
}
