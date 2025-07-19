package com.example.application.service;

import com.example.application.dto.chat.AiMessageDto;
import com.example.application.dto.chat.UserMessageDto;
import com.example.application.repository.ChatHistoryRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.core.publisher.Mono;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;

@Slf4j
@Service
@RequiredArgsConstructor
public class ChatService {

//    public AiMessageDto handleUserMessage(UserMessageDto userMessageDto) {
//        log.info("사용자 메시지 수신: {}", userMessageDto);
//
//        // 실제로는 FastAPI or LangChain API 호출 → AI 응답 받아오기
//        String response = "AI 응답: " + userMessageDto.getContent();
//
//        return AiMessageDto.builder()
//                .senderId("AI")
//                .receiverId(userMessageDto.getSenderId()) // 수신자 = 사용자
//                .content(response)
//                .timestamp(LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss")))
//                .messageType("text")
//                .build();
//    }


    private final ChatHistoryService chatHistoryService;
    private final WebClient webClient; // Bean 등록 필요

    public Mono<AiMessageDto> handleUserMessage(UserMessageDto userMessageDto, Long bookId) {
        // 사용자 메시지 저장
        chatHistoryService.saveUserMessage(userMessageDto, bookId);

        // LangChain에 요청하고 응답 저장
        return sendToLangChain(userMessageDto)
                .doOnNext(aiMessageDto ->
                        chatHistoryService.saveAiMessage(aiMessageDto,
                                Long.parseLong(userMessageDto.getSenderId()), bookId)
                );
    }

    private Mono<AiMessageDto> sendToLangChain(UserMessageDto userMessageDto) {
        return webClient.post()
                .uri("/api/chat") // FastAPI 내 API 경로
                .bodyValue(userMessageDto)
                .retrieve()
                .bodyToMono(AiMessageDto.class)
                .onErrorResume(error -> {
                    log.error("LangChain 호출 실패: {}", error.getMessage());
                    return Mono.just(AiMessageDto.builder()
                            .senderId("AI")
                            .receiverId(userMessageDto.getSenderId())
                            .content("AI 서버 응답에 실패했습니다.")
                            .timestamp(LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss")))
                            .messageType("text")
                            .build());
                });
    }
}
