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

    /**
     * 상태 기반 챗봇 흐름의 메인 진입 메서드
     * - 사용자 메시지를 받아 상태를 판단하고 LangChain 호출
     * - 응답을 저장 및 다음 상태 계산
     */
    public AiMessageDto handleChatFlow(UserMessageDto userMessageDto) {
        Long userId = Long.parseLong(userMessageDto.getUserId());
        Long bookId = userMessageDto.getBookId();

        // ✅ 현재 상태 확보: DTO에서 오지 않았다면 마지막 채팅 이력으로 fallback
        FeatureContext currentFeatureContext = Optional.ofNullable(userMessageDto.getFeatureContext())
                .or(() -> chatHistoryService.findLastMessage(userId, bookId).map(ChatHistory::getFeatureContext))
                .orElse(FeatureContext.INITIAL);

        StageContext currentStageContext = Optional.ofNullable(userMessageDto.getStageContext())
                .or(() -> chatHistoryService.findLastMessage(userId, bookId).map(ChatHistory::getStageContext))
                .orElse(StageContext.START);

        // 🧠 LangChain 호출 (FastAPI에게 현재 상태를 포함한 메시지 전달)
        AiMessageDto aiMessageDto = callLangChain(userMessageDto, currentFeatureContext, currentStageContext);

        // 🔁 다음 상태 계산 (현재 응답 기반으로 다음 상태 판단)
        FeatureContext nextFeatureContext = calculateNextFeatureContext(aiMessageDto, userMessageDto);
        StageContext nextStageContext = calculateNextStageContext(aiMessageDto, userMessageDto);

        // 📨 다음 상태를 UserMessageDto에 기록 (다음 요청 시 기준이 됨)
        userMessageDto.setFeatureContext(nextFeatureContext);
        userMessageDto.setStageContext(nextStageContext);

        // 💾 채팅 이력 저장 (기준은 현재 상태 - 응답이 아님)
        chatHistoryService.saveUserMessage(userMessageDto, currentFeatureContext, currentStageContext);
        chatHistoryService.saveAiMessage(aiMessageDto, userId, bookId);

        return aiMessageDto;
    }

    /**
     * LangChain 호출
     * - FastAPI에게 현재 상태를 포함한 UserMessageDto 전송
     * - 실패 시 기본 응답 반환
     */
    private AiMessageDto callLangChain(UserMessageDto dto,
                                       FeatureContext featureContext,
                                       StageContext stageContext) {
        // 현재 상태를 DTO에 설정하여 전송
        dto.setFeatureContext(featureContext);
        dto.setStageContext(stageContext);

        return webClient.post()
                .uri("/api/chat")
                .bodyValue(dto)
                .retrieve()
                .bodyToMono(AiMessageDto.class)
                .map(ai -> {
                    ai.setUserId(dto.getUserId());
                    ai.setBookId(dto.getBookId());
                    return ai;
                })
                .onErrorResume(e -> {
                    log.error("LangChain 호출 실패", e);
                    // 실패 응답 처리 (fallback)
                    return Mono.just(AiMessageDto.builder()
                            .userId(dto.getUserId())
                            .bookId(dto.getBookId())
                            .sender("AI")
                            .content("AI 응답 실패")
                            .messageType("TEXT")
                            .build());
                }).block(); // 동기 방식 처리
    }

    /**
     * 다음 FeatureContext (기능 단위) 계산
     * - 사용자 입력이 "처음으로", "다른 기능으로 돌아가기"인 경우 초기화
     * - 그 외에는 AI 응답의 stageContext 기준으로 기능 추론
     */
    private FeatureContext calculateNextFeatureContext(AiMessageDto ai, UserMessageDto user) {
        String userInput = user.getContent();

        // 🔁 사용자가 직접 초기화 요청한 경우
        if ("처음으로".equalsIgnoreCase(userInput) || "종료".equals(userInput)) {
            return FeatureContext.INITIAL;
        }

        // 🔀 AI 응답의 현재 단계(stageContext)에 따라 다음 기능 결정
        return switch (ai.getStageContext()) {

            // 초기 진입 or 기능 종료 후
            case START, PROMPT_NEXT_ACTION -> FeatureContext.INITIAL;

            // 문제 생성 흐름 (챕터/개념 선택, 생성 중 등)
            case SELECT_TYPE,
                 PROMPT_CHAPTER_PAGE,
                 PROMPT_CONCEPT,
                 GENERATING_PROBLEM -> FeatureContext.PROBLEM_GENERATION;

            // 문제 풀이 흐름 (문제 제시, 정답/오답 피드백 등)
            case PROBLEM_PRESENTED,
                 USER_ANSWER,
                 CORRECT_FEEDBACK,
                 INCORRECT_FEEDBACK -> FeatureContext.PROBLEM_SOLVING;

            // 개념 설명 및 피드백 흐름
            case EXPLANATION_PRESENTED,
                 FEEDBACK_RATING,
                 PROMPT_FEEDBACK_TEXT,
                 INPUT_FEEDBACK_TEXT,
                 RE_EXPLANATION_PRESENTED -> FeatureContext.CONCEPT_EXPLANATION;
        };
    }

    /**
     * 다음 StageContext (기능 내 단계) 계산
     * - 사용자 입력과 AI 응답의 현재 단계(stageContext)를 바탕으로 흐름 전이
     */
    private StageContext calculateNextStageContext(AiMessageDto ai, UserMessageDto user) {
        String userInput = user.getContent();

        // 🔁 사용자 요청으로 흐름을 초기화 (예: "처음으로", "종료")
        if ("처음으로".equalsIgnoreCase(userInput) || "종료".equalsIgnoreCase(userInput)) {
            return StageContext.START;
        }

        // 🔁 AI 응답 기준으로 다음 단계 결정
        return switch (ai.getStageContext()) {

            // 처음 진입: 기능 선택으로 유도
            case START -> StageContext.SELECT_TYPE;

            // 기능 선택지에 대한 사용자 응답
            case SELECT_TYPE -> {
                if ("1".equals(userInput)) yield StageContext.PROMPT_CHAPTER_PAGE;  // 챕터/페이지 선택
                else if ("2".equals(userInput)) yield StageContext.PROMPT_CONCEPT;  // 개념 입력 선택
                else yield StageContext.SELECT_TYPE;  // 잘못된 입력 → 반복
            }

            // 입력 이후 문제 생성 요청 단계로 전이
            case PROMPT_CHAPTER_PAGE, PROMPT_CONCEPT -> StageContext.GENERATING_PROBLEM;

            // 문제 생성 완료 후 문제 제시
            case GENERATING_PROBLEM -> StageContext.PROBLEM_PRESENTED;

            // 문제 제시 후 사용자 응답 대기
            case PROBLEM_PRESENTED -> StageContext.USER_ANSWER;

            // 사용자 응답을 받았지만 계속 문제 풀이 단계 유지
            case USER_ANSWER -> StageContext.USER_ANSWER;

            // 정답 피드백 이후 분기
            case CORRECT_FEEDBACK -> {
                if ("1".equals(userInput)) yield StageContext.PROBLEM_PRESENTED; // 다음 문제 계속
                else yield StageContext.PROMPT_NEXT_ACTION; // 기능 전환
            }

            // 오답 피드백 이후 분기
            case INCORRECT_FEEDBACK -> {
                if ("1".equals(userInput)) yield StageContext.EXPLANATION_PRESENTED; // 개념 설명 선택
                else if ("2".equals(userInput)) yield StageContext.PROBLEM_PRESENTED; // 다음 문제 선택
                else yield StageContext.PROMPT_NEXT_ACTION; // 잘못된 응답 → 기능 전환
            }

            // 개념 설명 후 → 이해도 평가
            case EXPLANATION_PRESENTED -> StageContext.FEEDBACK_RATING;

            // 이해도 점수 평가
            case FEEDBACK_RATING -> {
                try {
                    int score = Integer.parseInt(userInput);
                    if (score >= 4) yield StageContext.PROMPT_NEXT_ACTION; // 이해 완료
                    else yield StageContext.PROMPT_FEEDBACK_TEXT; // 부족 → 상세 피드백 요청
                } catch (NumberFormatException e) {
                    yield StageContext.FEEDBACK_RATING; // 숫자 아님 → 다시 요청
                }
            }

            // 피드백 작성 단계
            case PROMPT_FEEDBACK_TEXT -> StageContext.INPUT_FEEDBACK_TEXT;

            // 입력받은 피드백을 바탕으로 재설명
            case INPUT_FEEDBACK_TEXT -> StageContext.RE_EXPLANATION_PRESENTED;

            // 재설명 이후 다시 점수 요청
            case RE_EXPLANATION_PRESENTED -> StageContext.FEEDBACK_RATING;

            // 기능 종료 후 기능 선택 화면 복귀
            case PROMPT_NEXT_ACTION -> StageContext.SELECT_TYPE;
        };
    }
}
