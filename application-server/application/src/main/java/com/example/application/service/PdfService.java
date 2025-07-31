package com.example.application.service;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.core.io.ByteArrayResource;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Service;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.util.MultiValueMap;
import org.springframework.web.reactive.function.BodyInserters;
import org.springframework.web.reactive.function.client.WebClient;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpMethod;
import org.springframework.http.ResponseEntity;
import com.example.application.repository.BookRepository;
import com.example.application.entity.Book;

import java.util.Base64;
import java.util.Map;
import java.util.HashMap;
import java.time.LocalDateTime;

@Service
@RequiredArgsConstructor
@Slf4j
public class PdfService {

    private final WebClient webClient;
    private final BookRepository bookRepository;

    /**
     * PDF를 langchain-server로 전송하여 임베딩 처리 (비동기)
     */
    public void sendPdfToLangchainServerAsync(String pdfBase64, Long bookId, Long userId) {
        try {
            log.info("=== PDF 파일을 Langchain Server로 전송하여 임베딩 처리 중 ===");
            log.info("BookId: {}, UserId: {}", bookId, userId);
            
            // 임베딩 상태를 PROCESSING으로 업데이트
            updateEmbeddingStatus(bookId, "PROCESSING");
            
            // 요청 데이터 구성
            Map<String, Object> requestData = new HashMap<>();
            requestData.put("pdf_base64", pdfBase64);
            requestData.put("bookId", bookId);
            requestData.put("userId", userId);
            requestData.put("query", "Java 프로그래밍"); // 기본 쿼리
            requestData.put("max_pages", 20); // 최대 페이지 수
            
            // langchain-server의 RAG 엔드포인트 호출 (비동기)
            webClient.post()
                .uri("/generating-question")
                .contentType(MediaType.APPLICATION_JSON)
                .bodyValue(requestData)
                .retrieve()
                .bodyToMono(String.class)
                .subscribe(
                    response -> {
                        log.info("Langchain Server 임베딩 완료: {}", response);
                        updateEmbeddingStatus(bookId, "COMPLETED");
                    },
                    error -> {
                        log.error("Langchain Server 임베딩 오류: {}", error.getMessage());
                        updateEmbeddingStatus(bookId, "FAILED");
                    }
                );
        } catch (Exception e) {
            log.error("Langchain Server 호출 예외: {}", e.getMessage());
            updateEmbeddingStatus(bookId, "FAILED");
        }
    }

    /**
     * 임베딩 상태 업데이트
     */
    private void updateEmbeddingStatus(Long bookId, String status) {
        try {
            bookRepository.findById(bookId).ifPresent(book -> {
                book.setEmbeddingStatus(status);
                if ("COMPLETED".equals(status)) {
                    book.setEmbeddingCompletedAt(LocalDateTime.now());
                }
                bookRepository.save(book);
                log.info("임베딩 상태 업데이트: BookId={}, Status={}", bookId, status);
            });
        } catch (Exception e) {
            log.error("임베딩 상태 업데이트 실패: BookId={}, Error={}", bookId, e.getMessage());
        }
    }

    /**
     * 기존 메서드 (파일 업로드 방식) - 호환성 유지
     */
    public void sendPdfToFastApi(String pdfBase64) {
        try {
            log.info("=== PDF 파일을 FastAPI로 전송 중 ===");
            
            // Base64를 바이트 배열로 디코딩
            byte[] pdfBytes = Base64.getDecoder().decode(pdfBase64);
            
            // ByteArrayResource로 파일 생성
            ByteArrayResource pdfResource = new ByteArrayResource(pdfBytes) {
                @Override
                public String getFilename() {
                    return "document.pdf";
                }
            };
            
            // MultiValueMap으로 form-data 생성
            MultiValueMap<String, Object> formData = new LinkedMultiValueMap<>();
            formData.add("pdf_file", pdfResource);
            formData.add("query", "");
            formData.add("difficulty", "보통");
            formData.add("question_type", "객관식");
            formData.add("count", 1);

            webClient.post()
                .uri("/generating-question")
                .contentType(MediaType.MULTIPART_FORM_DATA)
                .body(BodyInserters.fromMultipartData(formData))
                .retrieve()
                .bodyToMono(String.class)
                .subscribe(
                    response -> log.info("FastAPI 응답: {}", response),
                    error -> log.error("FastAPI 오류: {}", error.getMessage())
                );
        } catch (Exception e) {
            log.error("FastAPI 호출 예외: {}", e.getMessage());
        }
    }
}