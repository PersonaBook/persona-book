package com.example.application.controller.pdf;

import com.example.application.entity.Book;
import com.example.application.repository.BookRepository;
import com.example.application.service.PdfService;
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
    private final PdfService pdfService;

    public PdfController(JwtAuthUtil jwtAuthUtil, BookRepository bookRepository, PdfService pdfService) {
        this.jwtAuthUtil = jwtAuthUtil;
        this.bookRepository = bookRepository;
        this.pdfService = pdfService;
    }

    @PostMapping("/api/pdf/upload")
    @ResponseBody
    public ResponseEntity<?> uploadPdf(@RequestBody Map<String, Object> requestData, HttpServletRequest request) {
        User user = authenticateUserForUpload(request);
        if (user == null) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body("인증 필요");
        }

        try {
            validateUploadRequest(requestData);
            Book savedBook = createAndSaveBook(requestData, user);
            
            // PDF를 langchain-server로 전송하여 임베딩 처리 (비동기)
            pdfService.sendPdfToLangchainServerAsync(
                savedBook.getFileBase64(),
                savedBook.getBookId(),
                savedBook.getUserId()
            );
            
            return ResponseEntity.ok(buildSuccessResponse(savedBook));
        } catch (IllegalArgumentException e) {
            return ResponseEntity.badRequest().body(e.getMessage());
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body("PDF 저장 실패: " + e.getMessage());
        }
    }
    
    private User authenticateUserForUpload(HttpServletRequest request) {
        return jwtAuthUtil.getUserFromRequest(request);
    }
    
    private void validateUploadRequest(Map<String, Object> requestData) {
        String title = (String) requestData.get("title");
        String fileBase64 = (String) requestData.get("file_base64");

        if (title == null || title.trim().isEmpty()) {
            throw new IllegalArgumentException("제목이 필요합니다");
        }

        if (fileBase64 == null || fileBase64.trim().isEmpty()) {
            throw new IllegalArgumentException("파일 데이터가 필요합니다");
        }
    }
    
    private Book createAndSaveBook(Map<String, Object> requestData, User user) {
        String title = (String) requestData.get("title");
        String fileBase64 = (String) requestData.get("file_base64");
        
        Book book = new Book();
        book.setUserId(user.getUserId());
        book.setTitle(title);
        book.setFileBase64(fileBase64);

        return bookRepository.save(book);
    }
    
    private Map<String, Object> buildSuccessResponse(Book savedBook) {
        Map<String, Object> response = new HashMap<>();
        response.put("success", true);
        response.put("message", "PDF 업로드 성공");
        response.put("bookId", savedBook.getBookId());
        return response;
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