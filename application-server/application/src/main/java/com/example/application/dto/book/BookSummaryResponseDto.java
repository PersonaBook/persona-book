package com.example.application.dto.book;

import com.example.application.entity.Book;
import java.time.LocalDateTime;

public record BookSummaryResponseDto(
        Long bookId,
        String title,
        LocalDateTime createdAt,
        String embeddingStatus
) {
    public static BookSummaryResponseDto from(Book b) {
        return new BookSummaryResponseDto(
                b.getBookId(),
                b.getTitle(),
                b.getCreatedAt(),
                b.getEmbeddingStatus()
        );
    }
}
