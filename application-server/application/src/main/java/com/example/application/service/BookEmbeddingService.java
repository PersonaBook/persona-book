package com.example.application.service;

import com.example.application.repository.BookRepository;
import com.example.application.type.EmbeddingState;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.core.io.ByteArrayResource;
import org.springframework.http.MediaType;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Propagation;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.util.MultiValueMap;
import org.springframework.web.reactive.function.BodyInserters;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.util.retry.Retry;

import java.time.Duration;
import java.util.Base64;

@Service
@RequiredArgsConstructor
@Slf4j
public class BookEmbeddingService {

    private final WebClient webClient;
    private final BookRepository bookRepository;

    private static final String FASTAPI_ENDPOINT = "/generating-question";
    private static final Duration HTTP_TIMEOUT = Duration.ofSeconds(600);


    @Async
    public void processEmbedding(Long bookId, String fileBase64) {
        log.info(">>> [Async] 임베딩 작업 시작 bookId={}", bookId);

        updateState(bookId, EmbeddingState.PROCESSING);

        try {
            ByteArrayResource pdfFile = decodePdf(fileBase64);

            MultiValueMap<String, Object> body = new LinkedMultiValueMap<>();
            body.add("pdf_file", pdfFile);
            body.add("bookId", bookId.toString());
            body.add("query", "Java 프로그래밍");
            body.add("max_pages", "20");
            body.add("difficulty", "보통");
            body.add("question_type", "객관식");
            body.add("count", "1");

            String response = webClient.post()
                    .uri(FASTAPI_ENDPOINT)
                    .contentType(MediaType.MULTIPART_FORM_DATA)
                    .body(BodyInserters.fromMultipartData(body))
                    .retrieve()
                    .bodyToMono(String.class)
                    .timeout(HTTP_TIMEOUT)
                    .retryWhen(Retry.backoff(2, Duration.ofSeconds(1)))
                    .block();

            log.info("FastAPI 응답 완료: {}", response);
            updateState(bookId, EmbeddingState.COMPLETED);

        } catch (Exception e) {
            log.error("임베딩 실패 bookId={}", bookId, e);
            updateState(bookId, EmbeddingState.FAILED);
        }
    }


    @Transactional(propagation = Propagation.REQUIRES_NEW)
    public void updateState(Long bookId, EmbeddingState state) {
        bookRepository.findById(bookId).ifPresent(book -> {
            book.updateEmbeddingState(state);
        });
    }


    private ByteArrayResource decodePdf(String fileBase64) {
        if (fileBase64 == null || fileBase64.isEmpty()) throw new IllegalArgumentException("Empty Base64");

        byte[] pdfBytes = Base64.getDecoder().decode(fileBase64);

        return new ByteArrayResource(pdfBytes) {
            @Override
            public String getFilename() { return "upload.pdf"; }
        };
    }
}