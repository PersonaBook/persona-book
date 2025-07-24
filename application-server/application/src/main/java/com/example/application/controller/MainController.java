package com.example.application.controller;

import com.example.application.service.PdfService;
import com.example.application.repository.BookRepository;
import com.example.application.entity.Book;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;
import com.example.application.util.JwtAuthUtil;
import com.example.application.entity.User;
import jakarta.servlet.http.HttpServletRequest;
import java.util.List;
import java.util.Map;
import java.util.HashMap;
import java.util.Optional;
import com.fasterxml.jackson.databind.ObjectMapper;

@Controller
public class MainController {

    @Autowired
    private PdfService pdfService;

    @Autowired
    private BookRepository bookRepository;

    @Autowired
    private JwtAuthUtil jwtAuthUtil;

    @Autowired
    private ObjectMapper objectMapper;

    @GetMapping({"/"})
    public String pdfMain(HttpServletRequest request, Model model) {
        System.out.println("=== 메인 페이지 요청 ===");
        String loginToken = (String) request.getSession().getAttribute("loginToken");
        System.out.println("세션 토큰: " + (loginToken != null ? "있음 - " + loginToken.substring(0, 20) + "..." : "없음"));
        if (loginToken != null) {
            System.out.println("토큰을 모델에 추가");
            model.addAttribute("loginToken", loginToken);
        }
        return "index";
    }

    @GetMapping("/pdf/detail/{bookId}")
    public String pdfDetail(@PathVariable Long bookId, HttpServletRequest request, Model model) {
        System.out.println("=== PDF Detail 요청 ===");
        System.out.println("BookId: " + bookId);
        
        User user = jwtAuthUtil.getUserFromRequest(request);
        System.out.println("User: " + (user != null ? user.getUserId() : "null"));
        
        if (user == null) {
            System.out.println("사용자 인증 실패 - 로그인 페이지로 리다이렉트");
            return "redirect:/user/login";
        }

        try {
            System.out.println("DB 쿼리 실행: userId=" + user.getUserId() + ", bookId=" + bookId);
            Optional<Book> bookOpt = bookRepository.findByBookIdAndUserIdAndDeletedAtIsNull(bookId, user.getUserId());
            
            if (bookOpt.isEmpty()) {
                System.out.println("책을 찾을 수 없음");
                model.addAttribute("errorMessage", "PDF를 찾을 수 없습니다.");
                return "error/404";
            }

            Book book = bookOpt.get();
            System.out.println("책 찾음: " + book.getTitle() + ", bookId=" + book.getBookId());
            System.out.println("fileBase64 존재: " + (book.getFileBase64() != null ? "YES" : "NO"));
            if (book.getFileBase64() != null) {
                System.out.println("fileBase64 길이: " + book.getFileBase64().length());
            }
            
            book.setLastAccessedAt(java.time.LocalDateTime.now());
            bookRepository.save(book);

            // Book 객체를 JSON으로 수동 직렬화
            String bookJson = objectMapper.writeValueAsString(book);
            model.addAttribute("book", book);
            model.addAttribute("bookJson", bookJson);
            System.out.println("bookJson 길이: " + bookJson.length());
            System.out.println("템플릿 반환: page/pdfDetail");
            return "page/pdfDetail";
        } catch (Exception e) {
            System.out.println("오류 발생: " + e.getMessage());
            e.printStackTrace();
            model.addAttribute("errorMessage", "PDF 로드에 실패했습니다: " + e.getMessage());
            return "error/500";
        }
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

    @GetMapping("/api/pdf/detail/{bookId}")
    @ResponseBody
    public ResponseEntity<?> getPdfDetail(@PathVariable Long bookId, HttpServletRequest request) {
        User user = jwtAuthUtil.getUserFromRequest(request);
        if (user == null) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body("인증 필요");
        }

        try {
            Optional<Book> bookOpt = bookRepository.findByBookIdAndUserIdAndDeletedAtIsNull(bookId, user.getUserId());
            if (bookOpt.isEmpty()) {
                return ResponseEntity.notFound().build();
            }

            Book book = bookOpt.get();
            book.setLastAccessedAt(java.time.LocalDateTime.now());
            bookRepository.save(book);

            return ResponseEntity.ok(book);
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body("PDF 상세 조회 실패: " + e.getMessage());
        }
    }
}