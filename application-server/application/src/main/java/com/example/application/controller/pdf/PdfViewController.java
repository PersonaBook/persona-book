package com.example.application.controller.pdf;

import com.example.application.entity.Book;
import com.example.application.entity.User;
import com.example.application.repository.BookRepository;
import com.example.application.service.PdfService;
import com.example.application.util.JwtAuthUtil;
import com.fasterxml.jackson.databind.ObjectMapper;
import jakarta.servlet.http.HttpServletRequest;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;

import java.util.Optional;

@Controller
public class PdfViewController {


    private final BookRepository bookRepository;

    private final JwtAuthUtil jwtAuthUtil;

    private final ObjectMapper objectMapper;

    private final com.example.application.service.PdfService pdfService;

    public PdfViewController(BookRepository bookRepository, JwtAuthUtil jwtAuthUtil, ObjectMapper objectMapper, PdfService pdfService) {
        this.bookRepository = bookRepository;
        this.jwtAuthUtil = jwtAuthUtil;
        this.objectMapper = objectMapper;
        this.pdfService = pdfService;
    }

    @GetMapping("/pdf/detail/{bookId}")
    public String pdfDetail(@PathVariable Long bookId, HttpServletRequest request, Model model) {
        System.out.println("=== PDF Detail 요청 ===");
        System.out.println("BookId: " + bookId);
        
        User user = authenticateUser(request);
        if (user == null) {
            return "redirect:/user/login";
        }
        
        try {
            Book book = findAndValidateBook(bookId, user.getUserId(), model);
            if (book == null) {
                return "index";
            }
            
            updateBookAccess(book);
            processPdfForFastApi(book);
            prepareModelAttributes(book, model);
            
            System.out.println("템플릿 반환: page/pdfDetail");
            return "page/pdfDetail";
        } catch (Exception e) {
            System.out.println("오류 발생: " + e.getMessage());
            e.printStackTrace();
            model.addAttribute("errorMessage", "PDF 로드에 실패했습니다: " + e.getMessage());
            return "error/500";
        }
    }
    
    private User authenticateUser(HttpServletRequest request) {
        User user = jwtAuthUtil.getUserFromRequest(request);
        System.out.println("User: " + (user != null ? user.getUserId() : "null"));
        
        if (user == null) {
            System.out.println("사용자 인증 실패 - 로그인 페이지로 리다이렉트");
        }
        return user;
    }
    
    private Book findAndValidateBook(Long bookId, Long userId, Model model) {
        System.out.println("DB 쿼리 실행: userId=" + userId + ", bookId=" + bookId);
        Optional<Book> bookOpt = bookRepository.findByBookIdAndUserIdAndDeletedAtIsNull(bookId, userId);
        
        if (bookOpt.isEmpty()) {
            System.out.println("책을 찾을 수 없음");
            model.addAttribute("errorMessage", "PDF를 찾을 수 없습니다.");
            return null;
        }
        
        Book book = bookOpt.get();
        System.out.println("책 찾음: " + book.getTitle() + ", bookId=" + book.getBookId());
        System.out.println("fileBase64 존재: " + (book.getFileBase64() != null ? "YES" : "NO"));
        if (book.getFileBase64() != null) {
            System.out.println("fileBase64 길이: " + book.getFileBase64().length());
        }
        return book;
    }
    
    private void updateBookAccess(Book book) {
        book.setLastAccessedAt(java.time.LocalDateTime.now());
        bookRepository.save(book);
    }
    
    private void processPdfForFastApi(Book book) {
        // FastAPI 전송 메서드 호출 (비동기)
        if (book.getFileBase64() != null) {
            pdfService.sendPdfToFastApi(book.getFileBase64());
        }
    }
    
    private void prepareModelAttributes(Book book, Model model) throws Exception {
        // Book 객체를 JSON으로 수동 직렬화
        String bookJson = objectMapper.writeValueAsString(book);
        model.addAttribute("book", book);
        model.addAttribute("bookJson", bookJson);
        System.out.println("bookJson 길이: " + bookJson.length());
    }


}
