// BookDetailResponse.java
package com.example.application.dto.book;

import com.example.application.entity.Book;
import java.time.LocalDateTime;

public record BookDetailResponseDto(
        Long bookId,
        String title,
        String fileBase64,
        LocalDateTime createdAt,
        LocalDateTime lastAccessedAt,
        String embeddingStatus
) {
    public static BookDetailResponseDto from(Book b) {
        return new BookDetailResponseDto(
                b.getBookId(),
                b.getTitle(),
                b.getFileBase64(),
                b.getCreatedAt(),
                b.getLastAccessedAt(),
                b.getEmbeddingStatus()
        );
    }
}
