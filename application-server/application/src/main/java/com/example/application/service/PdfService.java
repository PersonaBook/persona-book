package com.example.application.service;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;

@Service
@RequiredArgsConstructor
@Slf4j
public class PdfService {

    private final WebClient webClient;

    public void sendPdfToFastApi(String pdfBase64) {
        try {
            log.info("=== PDF 데이터를 FastAPI로 전송 중 ===");
            
            var requestBody = java.util.Map.of(
                "pdf_base64", pdfBase64,
                "query", ""
            );

            webClient.post()
                .uri("/generate-question")
                .bodyValue(requestBody)
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