package com.example.application.dto.book;

import com.example.application.entity.Book;
import lombok.*;
import java.time.LocalDateTime;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class BookSummaryResponseDto {
    private Long bookId;
    private String title;
    private LocalDateTime createdAt;
    private String embeddingStatus;

    public static BookSummaryResponseDto from(Book b) {
        return BookSummaryResponseDto.builder()
                .bookId(b.getBookId())
                .title(b.getTitle())
                .createdAt(b.getCreatedAt())
                .embeddingStatus(b.getEmbeddingStatus())
                .build();
    }
}
