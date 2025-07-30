package com.example.application.entity;

import jakarta.persistence.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "book")
public class Book {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "book_id")
    private Long bookId;

    @Column(name = "user_id", nullable = false)
    private Long userId;

    @Column(name = "title")
    private String title;

    @Column(name = "file_base64", columnDefinition = "LONGTEXT")
    private String fileBase64;

    @Column(name = "author")
    private String author;

    @Column(name = "total_pages")
    private Integer totalPages;

    @Column(name = "created_at")
    private LocalDateTime createdAt;

    @Column(name = "last_accessed_at")
    private LocalDateTime lastAccessedAt;

    @Column(name = "deleted_at")
    private LocalDateTime deletedAt;

    // 임베딩 상태 관련 필드 추가
    @Column(name = "embedding_status")
    private String embeddingStatus;

    @Column(name = "embedding_completed_at")
    private LocalDateTime embeddingCompletedAt;

    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
        lastAccessedAt = LocalDateTime.now();
    }

    @PreUpdate
    protected void onUpdate() {
        lastAccessedAt = LocalDateTime.now();
    }

    public Long getBookId() {
        return bookId;
    }

    public void setBookId(Long bookId) {
        this.bookId = bookId;
    }

    public Long getUserId() {
        return userId;
    }

    public void setUserId(Long userId) {
        this.userId = userId;
    }

    public String getTitle() {
        return title;
    }

    public void setTitle(String title) {
        this.title = title;
    }

    public String getFileBase64() {
        return fileBase64;
    }

    public void setFileBase64(String fileBase64) {
        this.fileBase64 = fileBase64;
    }

    public String getAuthor() {
        return author;
    }

    public void setAuthor(String author) {
        this.author = author;
    }

    public Integer getTotalPages() {
        return totalPages;
    }

    public void setTotalPages(Integer totalPages) {
        this.totalPages = totalPages;
    }

    public LocalDateTime getCreatedAt() {
        return createdAt;
    }

    public void setCreatedAt(LocalDateTime createdAt) {
        this.createdAt = createdAt;
    }

    public LocalDateTime getLastAccessedAt() {
        return lastAccessedAt;
    }

    public void setLastAccessedAt(LocalDateTime lastAccessedAt) {
        this.lastAccessedAt = lastAccessedAt;
    }

    public LocalDateTime getDeletedAt() {
        return deletedAt;
    }

    public void setDeletedAt(LocalDateTime deletedAt) {
        this.deletedAt = deletedAt;
    }

    // 임베딩 상태 관련 getter/setter 추가
    public String getEmbeddingStatus() {
        return embeddingStatus;
    }

    public void setEmbeddingStatus(String embeddingStatus) {
        this.embeddingStatus = embeddingStatus;
    }

    public LocalDateTime getEmbeddingCompletedAt() {
        return embeddingCompletedAt;
    }

    public void setEmbeddingCompletedAt(LocalDateTime embeddingCompletedAt) {
        this.embeddingCompletedAt = embeddingCompletedAt;
    }
}