package com.example.application.controller.pdf;

import com.example.application.entity.Book;
import com.example.application.repository.BookRepository;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.*;
import com.example.application.util.JwtAuthUtil;
import com.example.application.entity.User;
import jakarta.servlet.http.HttpServletRequest;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Controller
public class PdfController {

    private final JwtAuthUtil jwtAuthUtil;

    private final BookRepository bookRepository;

    public PdfController(JwtAuthUtil jwtAuthUtil, BookRepository bookRepository) {
        this.jwtAuthUtil = jwtAuthUtil;
        this.bookRepository = bookRepository;
    }

    @PostMapping("/api/pdf/upload")
    @ResponseBody
    public ResponseEntity<?> uploadPdf(@RequestBody Map<String, Object> requestData, HttpServletRequest request) {
        User user = jwtAuthUtil.getUserFromRequest(request);
        if (user == null) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body("인증 필요");
        }

        try {
            String title = (String) requestData.get("title");
            String fileBase64 = (String) requestData.get("file_base64");

            if (title == null || title.trim().isEmpty()) {
                return ResponseEntity.badRequest().body("제목이 필요합니다");
            }

            if (fileBase64 == null || fileBase64.trim().isEmpty()) {
                return ResponseEntity.badRequest().body("파일 데이터가 필요합니다");
            }

            Book book = new Book();
            book.setUserId(user.getUserId());
            book.setTitle(title);
            book.setFileBase64(fileBase64);

            Book savedBook = bookRepository.save(book);

            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("message", "PDF 업로드 성공");
            response.put("bookId", savedBook.getBookId());

            return ResponseEntity.ok(response);

        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body("PDF 저장 실패: " + e.getMessage());
        }
    }

    @GetMapping("/api/pdf/list")
    @ResponseBody
    public ResponseEntity<?> getPdfList(HttpServletRequest request) {
        User user = jwtAuthUtil.getUserFromRequest(request);
        if (user == null) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body("인증 필요");
        }

        try {
            List<Book> books = bookRepository.findByUserIdAndDeletedAtIsNull(user.getUserId());
            return ResponseEntity.ok(books);
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body("PDF 목록 조회 실패: " + e.getMessage());
        }
    }
}