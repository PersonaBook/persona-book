package com.example.application.service;

import com.example.application.entity.Book;
import com.example.application.repository.BookRepository;
import jakarta.transaction.Transactional;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.core.io.ByteArrayResource;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Service;
import org.springframework.transaction.support.TransactionTemplate;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.util.MultiValueMap;
import org.springframework.web.reactive.function.BodyInserters;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.util.retry.Retry;

import java.time.Duration;
import java.time.LocalDateTime;
import java.util.Base64;
import java.util.HashMap;
import java.util.Map;

@Service
@RequiredArgsConstructor
@Slf4j
public class BookService {

    private final WebClient webClient;
    private final BookRepository bookRepository;
    private final TransactionTemplate txTemplate;

    // ───────── 상수/설정 (필요시 @Value로 외부화) ─────────
    private static final String STATUS_PROCESSING = "PROCESSING";
    private static final String STATUS_COMPLETED = "COMPLETED";
    private static final String STATUS_FAILED = "FAILED";

    private static final Duration HTTP_TIMEOUT = Duration.ofSeconds(600); // PDF 처리에 충분한 시간 (10분)
    private static final int RETRIES = 2;
    private static final Duration RETRY_BACKOFF = Duration.ofSeconds(1);

    private static final String FASTAPI_ENDPOINT = "/generating-question";

    private static String safe(String s) { return s == null ? "" : s; }

    /**
     * 업로드 직후 비동기 임베딩 파이프라인 시작.
     * FastAPI의 multipart/form-data 요청 방식에 맞게 수정.
     */
    public void sendBookToFastApiAsync(String pdfBase64, Long bookId) {
        Book book = bookRepository.findById(bookId).orElse(null);
        if (book == null) {
            log.warn("임베딩 요청 실패: 존재하지 않는 bookId={}", bookId);
            return;
        }

        if (STATUS_PROCESSING.equalsIgnoreCase(safe(book.getEmbeddingStatus()))) {
            log.info("이미 임베딩 처리 중 → 스킵 bookId={}", bookId);
            return;
        }

        log.info("=== PDF 임베딩 요청 시작 === bookId={}", bookId);

        // 상태: PROCESSING
        setEmbeddingStatusTx(bookId, STATUS_PROCESSING, false);

        try {
            // Base64를 바이트 배열로 디코딩
            byte[] pdfBytes = Base64.getDecoder().decode(pdfBase64);

            // ByteArrayResource로 파일 데이터 준비
            ByteArrayResource pdfResource = new ByteArrayResource(pdfBytes) {
                @Override
                public String getFilename() {
                    return "document.pdf";
                }
            };

            // MultiValueMap으로 form-data 구성 (FastAPI의 파일 업로드 형식)
            MultiValueMap<String, Object> formData = new LinkedMultiValueMap<>();
            formData.add("pdf_file", pdfResource); // FastAPI의 @Form_data()에 매핑될 필드명
            formData.add("bookId", bookId.toString()); // Long을 String으로 변환
            formData.add("userId", book.getUser().getUserId().toString());
            formData.add("query", "Java 프로그래밍");
            formData.add("max_pages", "20");
            formData.add("difficulty", "보통");
            formData.add("question_type", "객관식");
            formData.add("count", "1");

            webClient.post()
                    .uri(FASTAPI_ENDPOINT)
                    .contentType(MediaType.MULTIPART_FORM_DATA)
                    .body(BodyInserters.fromMultipartData(formData))
                    .retrieve()
                    .onStatus(status -> status.isError(), resp -> resp.createException())
                    .toBodilessEntity()
                    .timeout(HTTP_TIMEOUT)
                    .retryWhen(Retry.backoff(RETRIES, RETRY_BACKOFF).filter(ex -> isRetryable(ex)))
                    .doOnSuccess(v -> {
                        log.info("임베딩 완료 bookId={}", bookId);
                        setEmbeddingStatusTx(bookId, STATUS_COMPLETED, true);
                    })
                    .doOnError(ex -> {
                        log.error("임베딩 실패 bookId={}, err={}", bookId, ex.toString());
                        setEmbeddingStatusTx(bookId, STATUS_FAILED, false);
                    })
                    .subscribe();

        } catch (Exception e) {
            log.error("PDF 디코딩 또는 API 호출 중 예외 발생: {}", e.getMessage());
            setEmbeddingStatusTx(bookId, STATUS_FAILED, false);
        }
    }

    private boolean isRetryable(Throwable ex) {
        String m = String.valueOf(ex.getMessage()).toLowerCase();
        return m.contains("timeout") || m.contains("connect") || m.contains("refused");
    }

    /**
     * 기존 메서드 (파일 업로드 방식) - 호환성 유지
     */
    public void sendBookToFastApi(String pdfBase64) {
        // 이 메서드는 기존 방식대로 유지
        try {
            byte[] pdfBytes = Base64.getDecoder().decode(pdfBase64);

            ByteArrayResource pdfResource = new ByteArrayResource(pdfBytes) {
                @Override public String getFilename() { return "document.pdf"; }
            };

            MultiValueMap<String, Object> form = new LinkedMultiValueMap<>();
            form.add("pdf_file", pdfResource);
            form.add("query", "");
            form.add("difficulty", "보통");
            form.add("question_type", "객관식");
            form.add("count", 1);

            webClient.post()
                    .uri("/generating-question")
                    .contentType(MediaType.MULTIPART_FORM_DATA)
                    .body(BodyInserters.fromMultipartData(form))
                    .retrieve()
                    .onStatus(status -> status.isError(), resp -> resp.createException())
                    .toBodilessEntity()
                    .doOnSuccess(v -> log.info("FastAPI 호출 성공 (MULTIPART)"))
                    .doOnError(ex -> log.error("FastAPI 호출 실패 (MULTIPART): {}", ex.toString()))
                    .subscribe();
        } catch (Exception e) {
            log.error("FastAPI 호출 예외(MULTIPART): {}", e.getMessage());
        }
    }

    /** 트랜잭션으로 안전하게 임베딩 상태 업데이트 */
    private void setEmbeddingStatusTx(Long bookId, String status, boolean setCompletedAt) {
        try {
            txTemplate.executeWithoutResult(tx -> {
                bookRepository.findById(bookId).ifPresent(b -> {
                    b.setEmbeddingStatus(status);
                    if (setCompletedAt) {
                        b.setEmbeddingCompletedAt(LocalDateTime.now());
                    }
                    bookRepository.save(b);
                });
            });
            log.info("임베딩 상태 업데이트 완료 bookId={}, status={}", bookId, status);
        } catch (Exception e) {
            log.error("임베딩 상태 업데이트 실패 bookId={}, status={}, err={}", bookId, status, e.toString());
        }
    }
}