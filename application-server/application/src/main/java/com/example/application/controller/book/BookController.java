package com.example.application.controller.book;

import com.example.application.dto.book.BookSummaryResponseDto;
import com.example.application.dto.book.BookUploadRequestDto;
import com.example.application.entity.Book;
import com.example.application.entity.User;
import com.example.application.repository.BookRepository;
import com.example.application.service.BookService;
import com.example.application.util.JwtAuthUtil;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

@RestController
@RequiredArgsConstructor
@RequestMapping("/api/books")
public class BookController {

    private final JwtAuthUtil jwtAuthUtil;
    private final BookRepository bookRepository;
    private final BookService bookService;

    @PostMapping
    public ResponseEntity<?> upload(@Valid @RequestBody BookUploadRequestDto req, HttpServletRequest request) {
        User user = jwtAuthUtil.getUserFromRequest(request);
        if (user == null) return ResponseEntity.status(401).body("인증 필요");

        Book book = new Book();
        book.setUser(user);              // 연관관계 세팅
        book.setTitle(req.getTitle());
        book.setFileBase64(req.getFileBase64());

        Book saved = bookRepository.save(book);

        // ✅ 서비스 시그니처(2개 파라미터)에 맞게 수정
        bookService.sendBookToFastApiAsync(
                saved.getFileBase64(),
                saved.getBookId()
        );

        Map<String, Object> response = new HashMap<>();
        response.put("success", true);
        response.put("message", "책 업로드 성공");
        response.put("bookId", saved.getBookId());
        return ResponseEntity.ok(response);
    }

    @GetMapping
    public ResponseEntity<?> list(HttpServletRequest request) {
        User user = jwtAuthUtil.getUserFromRequest(request);
        if (user == null) return ResponseEntity.status(401).body("인증 필요");

        List<Book> books = bookRepository.findByUserAndDeletedAtIsNull(user);
        List<BookSummaryResponseDto> result = books.stream().map(BookSummaryResponseDto::from).toList();
        return ResponseEntity.ok(result);
    }
}
