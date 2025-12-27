package com.example.application.domain.book.controller;

import com.example.application.domain.book.dto.response.BookDetailResponseDto;
import com.example.application.domain.user.entity.User;
import com.example.application.domain.book.service.BookService;
import com.example.application.global.util.JwtAuthUtil;
import jakarta.servlet.http.HttpServletRequest;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;

@Slf4j
@Controller
@RequiredArgsConstructor
public class BookViewController {

    private final BookService bookService;
    private final JwtAuthUtil jwtAuthUtil;

    @GetMapping("/book/{bookId}")
    public String getBookPage(@PathVariable Long bookId, HttpServletRequest servletRequest, Model model) {
        User user = jwtAuthUtil.getUserFromRequest(servletRequest);
        if (user == null) return "redirect:/user/login";

        try {
            BookDetailResponseDto viewDto = bookService.getBookDetail(bookId, user);

            model.addAttribute("book", viewDto);

            return "page/book";

        } catch (IllegalArgumentException e) {
            model.addAttribute("errorMessage", e.getMessage());
            return "home";
        } catch (Exception e) {
            log.error("상세 조회 오류", e);
            model.addAttribute("errorMessage", "오류 발생");
            return "error/500";
        }
    }
}