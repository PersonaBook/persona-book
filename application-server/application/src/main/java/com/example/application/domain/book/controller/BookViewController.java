package com.example.application.domain.book.controller;

import com.example.application.domain.book.dto.response.BookDetailResponseDto;
import com.example.application.domain.book.service.BookService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestAttribute;

@Slf4j
@Controller
@RequiredArgsConstructor
public class BookViewController {

    private final BookService bookService;

    @GetMapping("/book/{bookId}")
    public String getBookPage(
            @PathVariable Long bookId,
            @RequestAttribute("userId") Long userId,
            Model model
    ) {
        BookDetailResponseDto bookDetail = bookService.getBookDetail(bookId, userId);
        model.addAttribute("book", bookDetail);
        return "page/book";
    }
}