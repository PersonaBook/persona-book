package com.example.application.dto.book;

import com.example.application.entity.Book;
import lombok.*;
import java.time.LocalDateTime;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class BookDetailResponseDto {
    private Long bookId;
    private String title;
    private String fileBase64;
    private LocalDateTime createdAt;
    private LocalDateTime lastAccessedAt;
    private String embeddingStatus;

    public static BookDetailResponseDto from(Book b) {
        return BookDetailResponseDto.builder()
                .bookId(b.getBookId())
                .title(b.getTitle())
                .fileBase64(b.getFileBase64())
                .createdAt(b.getCreatedAt())
                .lastAccessedAt(b.getLastAccessedAt())
                .embeddingStatus(b.getEmbeddingStatus())
                .build();
    }
}
