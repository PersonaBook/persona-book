package com.example.application.service;

import com.example.application.entity.Book;
import com.example.application.repository.BookRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatusCode;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Service;
import org.springframework.transaction.support.TransactionTemplate;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.util.retry.Retry;

import java.time.Duration;
import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.Map;

@Service
@RequiredArgsConstructor
@Slf4j
public class BookService {

    private final WebClient webClient;
    private final BookRepository bookRepository;
    private final TransactionTemplate txTemplate; // Reactive 콜백 안 상태변경 트랜잭션 보장

    // ───────── 상수/설정 (필요시 @Value로 외부화) ─────────
    private static final String STATUS_PROCESSING = "PROCESSING";
    private static final String STATUS_COMPLETED  = "COMPLETED";
    private static final String STATUS_FAILED     = "FAILED";

    private static final Duration HTTP_TIMEOUT  = Duration.ofSeconds(30);
    private static final int      RETRIES       = 2;
    private static final Duration RETRY_BACKOFF = Duration.ofSeconds(1);

    private static final String FASTAPI_ENDPOINT = "/generating-question";

    private static String safe(String s) { return s == null ? "" : s; }

    /**
     * 업로드 직후 비동기 임베딩 파이프라인 시작.
     * 컨트롤러 시그니처:
     *   bookService.sendBookToFastApiAsync(saved.getFileBase64(), saved.getBookId());
     */
    public void sendBookToFastApiAsync(String pdfBase64, Long bookId) {
        // Book 및 userId 확보 (연관관계 활용)
        Book book = bookRepository.findById(bookId).orElse(null);
        if (book == null) {
            log.warn("임베딩 요청 실패: 존재하지 않는 bookId={}", bookId);
            return;
        }
        Long userId = book.getUser().getUserId();

        // 이미 처리중이면 중복 실행 방지
        if (STATUS_PROCESSING.equalsIgnoreCase(safe(book.getEmbeddingStatus()))) {
            log.info("이미 임베딩 처리중 → 스킵 bookId={}", bookId);
            return;
        }

        log.info("=== PDF 임베딩 요청 시작 === bookId={}, userId={}", bookId, userId);

        // 상태: PROCESSING
        setEmbeddingStatusTx(bookId, STATUS_PROCESSING, false);

        // 요청 페이로드(JSON) — FastAPI가 bookId/userId를 필요로 할 수 있어 포함
        Map<String, Object> requestData = new HashMap<>();
        requestData.put("pdf_base64", pdfBase64);
        requestData.put("bookId", bookId);
        requestData.put("userId", userId);
        requestData.put("query", "Java 프로그래밍"); // 필요 시 외부화
        requestData.put("max_pages", 20);

        webClient.post()
                .uri(FASTAPI_ENDPOINT)
                .contentType(MediaType.APPLICATION_JSON)
                .bodyValue(requestData)
                .retrieve()
                .onStatus(HttpStatusCode::isError, resp -> resp.createException())
                .toBodilessEntity()
                .timeout(HTTP_TIMEOUT)
                .retryWhen(
                        Retry.backoff(RETRIES, RETRY_BACKOFF)
                                .filter(ex -> {
                                    String m = String.valueOf(ex.getMessage()).toLowerCase();
                                    return m.contains("timeout") || m.contains("connect") || m.contains("refused");
                                })
                                .onRetryExhaustedThrow((spec, signal) -> signal.failure())
                )
                .doOnSuccess(v -> {
                    log.info("임베딩 완료 bookId={}", bookId);
                    setEmbeddingStatusTx(bookId, STATUS_COMPLETED, true);
                })
                .doOnError(ex -> {
                    log.error("임베딩 실패 bookId={}, err={}", bookId, ex.toString());
                    setEmbeddingStatusTx(bookId, STATUS_FAILED, false);
                })
                .subscribe();
    }

    /**
     * (뷰에서 간단 호출) 레거시/데모용 — 단순 JSON 호출로 유지
     * BookViewController.detail()에서 사용:
     *   bookService.sendBookToFastApi(book.getFileBase64());
     */
    public void sendBookToFastApi(String pdfBase64) {
        try {
            byte[] pdfBytes = java.util.Base64.getDecoder().decode(pdfBase64);

            org.springframework.core.io.ByteArrayResource pdfResource =
                    new org.springframework.core.io.ByteArrayResource(pdfBytes) {
                        @Override public String getFilename() { return "document.pdf"; }
                    };

            org.springframework.util.MultiValueMap<String, Object> form = new org.springframework.util.LinkedMultiValueMap<>();
            form.add("pdf_file", pdfResource);   // ★ FastAPI에서 기대하던 필드명 유지
            form.add("query", "");
            form.add("difficulty", "보통");
            form.add("question_type", "객관식");
            form.add("count", 1);

            webClient.post()
                    .uri("/generating-question")
                    .contentType(org.springframework.http.MediaType.MULTIPART_FORM_DATA)
                    .body(org.springframework.web.reactive.function.BodyInserters.fromMultipartData(form))
                    .retrieve()
                    .onStatus(org.springframework.http.HttpStatusCode::isError, resp -> resp.createException())
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
                    bookRepository.save(b); // 명시 저장(더티체킹에 맡겨도 됨)
                });
            });
            log.info("임베딩 상태 업데이트 완료 bookId={}, status={}", bookId, status);
        } catch (Exception e) {
            log.error("임베딩 상태 업데이트 실패 bookId={}, status={}, err={}", bookId, status, e.toString());
        }
    }
}
