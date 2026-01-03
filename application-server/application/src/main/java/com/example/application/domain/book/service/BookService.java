package com.example.application.domain.book.service;

import com.example.application.domain.book.dto.request.BookUploadRequestDto;
import com.example.application.domain.book.dto.response.BookDetailResponseDto;
import com.example.application.domain.book.dto.response.BookSummaryResponseDto;
import com.example.application.domain.book.entity.Book;
import com.example.application.domain.book.repository.BookRepository;
import com.example.application.domain.book.type.EmbeddingState;
import com.example.application.domain.user.entity.User;
import com.example.application.domain.user.repository.UserRepository;
import com.example.application.global.exception.CustomException;
import com.example.application.global.exception.ErrorCode;
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
    private final UserRepository userRepository;
    private final BookEmbeddingService bookEmbeddingService;

    @Transactional
    public BookSummaryResponseDto uploadBook(Long userId, BookUploadRequestDto request) {
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new CustomException(ErrorCode.USER_NOT_FOUND));

        Book book = Book.builder()
                .user(user)
                .title(request.getTitle())
                .fileBase64(request.getFileBase64())
                .embeddingState(EmbeddingState.PENDING)
                .build();

        Book savedBook = bookRepository.save(book);

        bookEmbeddingService.processEmbedding(savedBook.getBookId(), userId, request.getFileBase64());

        return BookSummaryResponseDto.from(savedBook);
    }

    @Transactional(readOnly = true)
    public List<BookSummaryResponseDto> getBookList(Long userId) {
        return bookRepository.findAllByUser_UserId(userId)
                .stream()
                .map(BookSummaryResponseDto::from)
                .toList();
    }

    @Transactional(readOnly = true)
    public BookDetailResponseDto getBookDetail(Long bookId, Long userId) {
        Book book = bookRepository.findByBookIdAndUser_UserId(bookId, userId)
                .orElseThrow(() -> new CustomException(ErrorCode.BOOK_NOT_FOUND));

        return BookDetailResponseDto.from(book);
    }
}