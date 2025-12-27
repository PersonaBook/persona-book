package com.example.application.domain.book.controller;

import com.example.application.domain.book.dto.response.BookSummaryResponseDto;
import com.example.application.domain.book.dto.request.BookUploadRequestDto;
import com.example.application.domain.user.entity.User;
import com.example.application.domain.book.service.BookService;
import com.example.application.global.util.JwtAuthUtil;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequiredArgsConstructor
@RequestMapping("/api/book")
public class BookController {

    private final JwtAuthUtil jwtAuthUtil;
    private final BookService bookService;

    @PostMapping("/upload")
    public ResponseEntity<BookSummaryResponseDto> uploadBook(@Valid @RequestBody BookUploadRequestDto request, HttpServletRequest servletRequest) {
        User user = jwtAuthUtil.getUserFromRequest(servletRequest);

        if (user == null) return ResponseEntity.status(401).build();

        BookSummaryResponseDto response = bookService.uploadBook(user, request);

        return ResponseEntity.ok(response);
    }

    @GetMapping("/list")
    public ResponseEntity<List<BookSummaryResponseDto>> getBookList(HttpServletRequest servletRequest) {
        User user = jwtAuthUtil.getUserFromRequest(servletRequest);

        if (user == null) return ResponseEntity.status(401).build();

        List<BookSummaryResponseDto> books = bookService.getBookList(user);

        return ResponseEntity.ok(books);
    }
}
