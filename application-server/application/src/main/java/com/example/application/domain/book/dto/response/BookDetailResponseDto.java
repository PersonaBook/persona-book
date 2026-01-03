package com.example.application.domain.book.dto.response;

import com.example.application.domain.book.entity.Book;
import com.example.application.domain.book.type.EmbeddingState;
import lombok.*;
import java.time.LocalDateTime;

@Getter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class BookDetailResponseDto {
    private Long bookId;
    private Long userId;
    private String title;
    private String fileBase64;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
    private EmbeddingState embeddingState;

    public static BookDetailResponseDto from(Book book) {
        return BookDetailResponseDto.builder()
                .bookId(book.getBookId())
                .userId(book.getUser() != null ? book.getUser().getUserId() : null)
                .title(book.getTitle())
                .fileBase64(book.getFileBase64())
                .createdAt(book.getCreatedAt())
                .updatedAt(book.getUpdatedAt())
                .embeddingState(book.getEmbeddingState())
                .build();
    }
}
