// BookViewController.java
package com.example.application.controller.book;

import com.example.application.dto.book.BookDetailResponseDto;
import com.example.application.entity.Book;
import com.example.application.entity.User;
import com.example.application.repository.BookRepository;
import com.example.application.service.BookService;
import com.example.application.util.JwtAuthUtil;
import com.fasterxml.jackson.databind.ObjectMapper;
import jakarta.servlet.http.HttpServletRequest;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;

import java.time.LocalDateTime;
import java.util.Optional;

@Slf4j
@Controller
@RequiredArgsConstructor
public class BookViewController {

    private final BookRepository bookRepository;
    private final JwtAuthUtil jwtAuthUtil;
    private final ObjectMapper objectMapper;
    private final BookService bookService;

    // 레거시 경로 유지 + 신규 경로 병행(원하면 하나만 남겨도 OK)
    @GetMapping({"/book/detail/{bookId}", "/pdf/detail/{bookId}"})
    public String detail(@PathVariable Long bookId, HttpServletRequest request, Model model) {
        log.info("=== Book Detail 요청: bookId={} ===", bookId);

        User user = jwtAuthUtil.getUserFromRequest(request);
        if (user == null) {
            log.warn("인증 실패 → 로그인 페이지로 리다이렉트");
            return "redirect:/user/login";
        }

        try {
            // ✅ 레포 메서드 최신 시그니처로 교체
            Optional<Book> bookOpt =
                    bookRepository.findByBookIdAndUser_UserIdAndDeletedAtIsNull(bookId, user.getUserId());

            if (bookOpt.isEmpty()) {
                log.warn("도서 없음/권한 없음: bookId={}, userId={}", bookId, user.getUserId());
                model.addAttribute("errorMessage", "도서를 찾을 수 없습니다.");
                return "index";
            }

            Book book = bookOpt.get();

            // 마지막 접근 시각 업데이트
            book.setLastAccessedAt(LocalDateTime.now());
            bookRepository.save(book);

            // 필요 시 FastAPI 전송 (비동기)
            if (book.getFileBase64() != null) {
                bookService.sendBookToFastApi(book.getFileBase64());
            }

            // ✅ 엔티티 → DTO 변환 후 JSON (순환참조/LAZY 안전)
            BookDetailResponseDto viewDto = BookDetailResponseDto.from(book);
            String bookJson = objectMapper.writeValueAsString(viewDto);

            model.addAttribute("book", viewDto);
            model.addAttribute("bookJson", bookJson);

            // ✅ 템플릿 명: book-detail
            return "book-detail";

        } catch (Exception e) {
            log.error("상세 조회 오류", e);
            model.addAttribute("errorMessage", "책 로드에 실패했습니다: " + e.getMessage());
            return "error/500";
        }
    }
}
