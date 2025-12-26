package com.example.application.service;

import com.example.application.dto.book.request.BookUploadRequestDto;
import com.example.application.dto.book.response.BookDetailResponseDto;
import com.example.application.dto.book.response.BookSummaryResponseDto;
import com.example.application.entity.Book;
import com.example.application.entity.User;
import com.example.application.repository.BookRepository;
import com.example.application.type.EmbeddingState;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
@RequiredArgsConstructor
@Slf4j
public class BookService {

    private final BookRepository bookRepository;
    private final BookEmbeddingService bookEmbeddingService;

    @Transactional
    public BookSummaryResponseDto uploadBook(User user, BookUploadRequestDto request) {
        Book book = Book.builder()
                .user(user)
                .title(request.getTitle())
                .fileBase64(request.getFileBase64())
                .embeddingState(EmbeddingState.PENDING)
                .build();

        Book savedBook = bookRepository.save(book);

        bookEmbeddingService.processEmbedding(savedBook.getBookId(), request.getFileBase64());

        return BookSummaryResponseDto.from(savedBook);
    }

    @Transactional(readOnly = true)
    public List<BookSummaryResponseDto> getBookList(User user) {
        return bookRepository.findByUser(user)
                .stream()
                .map(BookSummaryResponseDto::from)
                .toList();
    }

    @Transactional(readOnly = true)
    public BookDetailResponseDto getBookDetail(Long bookId, User user) {
        Book book = bookRepository.findByBookIdAndUser(bookId, user)
                .orElseThrow(() -> new IllegalArgumentException("도서를 찾을 수 없습니다."));

        return BookDetailResponseDto.from(book);
    }
}