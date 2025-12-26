package com.example.application.entity;

import jakarta.persistence.*;
import lombok.*;
import org.hibernate.annotations.CreationTimestamp;
import org.hibernate.annotations.UpdateTimestamp;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.HashSet;
import java.util.Set;

@Getter
@NoArgsConstructor
@AllArgsConstructor
@Builder
@Entity
@Table(name = "user")
public class User {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "user_id")
    private Long userId;

    @Column(nullable = false, unique = true, length = 50)
    private String name;

    @Column(nullable = false, unique = true, length = 100)
    private String email;

    @Column(nullable = false, length = 15)
    private String phoneNumber;

    @Column(name = "birth_date")
    private LocalDate birthDate;

    @Column(name = "job")
    private String job;

    @Column(nullable = false)
    private String password;

    @Column(name = "created_at", updatable = false)
    private LocalDateTime createdAt;

    @Column(name = "updated_at")
    private LocalDateTime updatedAt;

    // ─────────────── 라이프사이클 메서드 ───────────────
    @PrePersist
    protected void onCreate() {
        this.createdAt = LocalDateTime.now();
        this.updatedAt = LocalDateTime.now();
    }

    @PreUpdate
    protected void onUpdate() {
        this.updatedAt = LocalDateTime.now();
    }

    // ─────────────── 연관관계 (역방향) ───────────────
    // 역방향 매핑은 필요한 경우에만 사용
    // 데이터가 많아질 경우, 성능 저하
//    @Builder.Default
//    @OneToMany(mappedBy = "user", fetch = FetchType.LAZY)
//    private Set<Book> books = new HashSet<>();
//
//    @Builder.Default
//    @OneToMany(mappedBy = "user", fetch = FetchType.LAZY)
//    private Set<Question> questions = new HashSet<>();
//
//    @Builder.Default
//    @OneToMany(mappedBy = "user", fetch = FetchType.LAZY)
//    private Set<ChatHistory> chatHistories = new HashSet<>();
}
