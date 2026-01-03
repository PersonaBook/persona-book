package com.example.application.domain.book.dto.response;

import com.example.application.domain.book.entity.Book;
import com.example.application.domain.book.type.EmbeddingState;
import lombok.*;
import java.time.LocalDateTime;

@Getter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class BookSummaryResponseDto {
    private Long bookId;
    private String title;
    private LocalDateTime createdAt;
    private EmbeddingState embeddingState;

    public static BookSummaryResponseDto from(Book book) {
        return BookSummaryResponseDto.builder()
                .bookId(book.getBookId())
                .title(book.getTitle())
                .createdAt(book.getCreatedAt())
                .embeddingState(book.getEmbeddingState())
                .build();
    }
}
