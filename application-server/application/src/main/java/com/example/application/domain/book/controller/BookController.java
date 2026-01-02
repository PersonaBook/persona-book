package com.example.application.domain.book.controller;

import com.example.application.domain.book.dto.request.BookUploadRequestDto;
import com.example.application.domain.book.dto.response.BookDetailResponseDto;
import com.example.application.domain.book.dto.response.BookSummaryResponseDto;
import com.example.application.domain.book.service.BookService;
import com.example.application.global.dto.ApiResponseDto;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequiredArgsConstructor
@RequestMapping("/api/book")
public class BookController {

    private final BookService bookService;

    @PostMapping("/upload")
    public ApiResponseDto<BookSummaryResponseDto> uploadBook(
            @RequestAttribute("userId") Long userId,
            @Valid @RequestBody BookUploadRequestDto request
    ) {
        return ApiResponseDto.success(bookService.uploadBook(userId, request));
    }

    @GetMapping("/list")
    public ApiResponseDto<List<BookSummaryResponseDto>> getBookList(
            @RequestAttribute("userId") Long userId
    ) {
        return ApiResponseDto.success(bookService.getBookList(userId));
    }

    @GetMapping("/api/book/detail/{bookId}")
    @ResponseBody
    public ApiResponseDto<BookDetailResponseDto> getBookDetailApi(
            @PathVariable Long bookId,
            @RequestAttribute("userId") Long userId // userId는 인증 인터셉터에서 주입됨
    ) {
        return ApiResponseDto.success(bookService.getBookDetail(bookId, userId));
    }
}