package com.example.application.service;

import com.example.application.dto.chat.AiMessageDto;
import com.example.application.dto.chat.UserMessageDto;
import com.example.application.entity.ChatHistory;
import com.example.application.entity.ChatHistory.FeatureContext;
import com.example.application.entity.ChatHistory.StageContext;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.core.publisher.Mono;

import java.util.Optional;

@Service
@RequiredArgsConstructor
@Slf4j
public class ChatService {

    private final ChatHistoryService chatHistoryService;
    private final WebClient webClient;

    public AiMessageDto handleChatFlow(UserMessageDto userMessageDto) {
        Long userId = Long.parseLong(userMessageDto.getUserId());
        Long bookId = userMessageDto.getBookId();

        // 최신 채팅 이력 확인
        Optional<ChatHistory> lastChatHistory = chatHistoryService.findLastMessage(userId, bookId);

        FeatureContext featureContext;
        StageContext stageContext;

        if (lastChatHistory.isEmpty()) {
            featureContext = FeatureContext.INITIAL;
            stageContext = StageContext.START;
        } else {
            featureContext = lastChatHistory.get().getFeatureContext();
            stageContext = lastChatHistory.get().getStageContext();
        }

        // LangChain 호출: UserMessageDto를 그대로 전달
        AiMessageDto aiMessage = callLangChain(userMessageDto, featureContext, stageContext);

        // 채팅 이력 저장
        chatHistoryService.saveUserMessage(userMessageDto, featureContext, stageContext);
        chatHistoryService.saveAiMessage(aiMessage, userId, bookId);

        return aiMessage;
    }

    private AiMessageDto callLangChain(UserMessageDto dto,
                                       ChatHistory.FeatureContext featureContext,
                                       ChatHistory.StageContext stageContext) {
        return webClient.post()
                .uri("/api/chat")
                .bodyValue(dto)
                .retrieve()
                .bodyToMono(AiMessageDto.class)
                .map(ai -> {
                    ai.setFeatureContext(featureContext);
                    ai.setStageContext(stageContext);
                    return ai;
                })
                .onErrorResume(e -> {
                    log.error("LangChain 실패", e);
                    return Mono.just(AiMessageDto.builder()
                            .userId(dto.getUserId())
                            .bookId(dto.getBookId())
                            .sender("AI")
                            .content("AI 응답 실패")
                            .messageType("TEXT")
                            .featureContext(featureContext)
                            .stageContext(stageContext)
                            .build());
                }).block();
    }
}