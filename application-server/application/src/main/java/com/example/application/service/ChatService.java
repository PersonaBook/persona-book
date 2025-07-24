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

import java.util.Map;
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

//        // 🧠 LangChain 호출 (FastAPI에게 현재 상태를 포함한 메시지 전달)
//        AiMessageDto aiMessageDto = callLangChain(userMessageDto, currentFeatureContext, currentStageContext);
//
//        // 🔁 다음 상태 계산 (현재 응답 기반으로 다음 상태 판단)
//        FeatureContext nextFeatureContext = calculateNextFeatureContext(aiMessageDto, userMessageDto, currentStageContext);
//        StageContext nextStageContext = calculateNextStageContext(aiMessageDto, userMessageDto, currentStageContext);
//
//        // 📨 AI 응답에 다음 상태 설정
//        aiMessageDto.setFeatureContext(nextFeatureContext);
//        aiMessageDto.setStageContext(nextStageContext);
//
//        // 💾 채팅 이력 저장 (사용자 메시지는 현재 상태, AI 메시지는 다음 상태로 저장)
//        chatHistoryService.saveUserMessage(userMessageDto, currentFeatureContext, currentStageContext);
//        chatHistoryService.saveAiMessage(aiMessageDto, userId, bookId);

        userMessageDto.setFeatureContext(currentFeatureContext);
        userMessageDto.setStageContext(currentStageContext);

        AiMessageDto aiMessageDto = callLangChain(userMessageDto);
        aiMessageDto.setUserId(userMessageDto.getUserId());
        aiMessageDto.setBookId(userMessageDto.getBookId());

        chatHistoryService.saveUserMessage(userMessageDto, currentFeatureContext, currentStageContext);
        chatHistoryService.saveAiMessage(aiMessageDto, userId, bookId);

        return aiMessageDto;
    }

    private AiMessageDto callLangChain(UserMessageDto dto) {
        return webClient.post()
                .uri("/chat")
                .bodyValue(dto)
                .retrieve()
                .bodyToMono(AiMessageDto.class)
                .onErrorResume(e -> {
                    log.error("FastAPI 호출 실패", e);
                    return Mono.just(AiMessageDto.builder()
                            .userId(dto.getUserId())
                            .bookId(dto.getBookId())
                            .content("⚠️ FastAPI 응답에 실패했습니다. 다시 시도해주세요.")
                            .messageType("TEXT")
                            .featureContext(dto.getFeatureContext())
                            .stageContext(dto.getStageContext())
                            .build());
                })
                .block();
    }

    public boolean checkLangChainConnection() {
        try {
            // 가벼운 빈 요청을 보내 LangChain FastAPI 응답 확인
            return webClient.post()
                    .uri("/chat") // FastAPI 쪽 chat 핸들러
                    .bodyValue(Map.of(
                            "userId", "ping", "bookId", 0,
                            "content", "ping", "sender", "USER",
                            "messageType", "TEXT",
                            "featureContext", "INITIAL",
                            "stageContext", "START"
                    ))
                    .retrieve()
                    .toBodilessEntity()
                    .block()
                    .getStatusCode()
                    .is2xxSuccessful();
        } catch (Exception e) {
            return false;
        }
    }

//    /**
//     * LangChain 호출
//     * - FastAPI에게 현재 상태를 포함한 UserMessageDto 전송
//     * - 실패 시 기본 응답 반환
//     */
//    private AiMessageDto callLangChain(UserMessageDto dto,
//                                       FeatureContext featureContext,
//                                       StageContext stageContext) {
//        // 현재 상태를 DTO에 설정하여 전송
//        dto.setFeatureContext(featureContext);
//        dto.setStageContext(stageContext);
//
//        return webClient.post()
//                .uri("/chat")
//                .bodyValue(dto)
//                .retrieve()
//                .bodyToMono(AiMessageDto.class)
//                .map(ai -> {
//                    ai.setUserId(dto.getUserId());
//                    ai.setBookId(dto.getBookId());
//                    return ai;
//                })
//                .onErrorResume(e -> {
//                    log.error("LangChain 호출 실패", e);
//                    // 실패 응답 처리 (fallback)
//                    return Mono.just(createFallbackResponse(dto, featureContext, stageContext));
//                }).block(); // 동기 방식 처리
//    }
//
//    /**
//     * FastAPI 호출 실패 시 기본 응답 생성
//     */
//    private AiMessageDto createFallbackResponse(UserMessageDto dto,
//                                                FeatureContext featureContext,
//                                                StageContext stageContext) {
//        String fallbackContent = switch (stageContext) {
//            case START -> "안녕하세요! 학습을 도와드리는 챗봇입니다.\n\n무엇을 도와드릴까요?\n1. 예상 문제 생성\n2. 페이지 찾기\n3. 학습 보충";
//            case SELECT_TYPE -> "예상 문제 생성을 선택하셨군요!\n\n어떤 기준으로 문제를 생성해 드릴까요?\n1. 챕터/페이지 범위\n2. 특정 개념";
//            case PROMPT_CHAPTER_PAGE -> "챕터나 페이지 범위를 알려주세요.\n\n예: 챕터 3 또는 150-160페이지";
//            case PROMPT_CONCEPT -> "어떤 개념에 대한 예상 문제를 원하시나요?\n\n예: 객체지향, 데이터베이스 등";
//            default -> "죄송합니다. 일시적인 오류가 발생했습니다. 다시 시도해 주세요.";
//        };
//
//        return AiMessageDto.builder()
//                .userId(dto.getUserId())
//                .bookId(dto.getBookId())
//                .sender("AI")
//                .content(fallbackContent)
//                .messageType("TEXT")
//                .featureContext(featureContext)
//                .stageContext(stageContext)
//                .build();
//    }

//    /**
//     * 다음 FeatureContext (기능 단위) 계산
//     */
//    private FeatureContext calculateNextFeatureContext(AiMessageDto ai, UserMessageDto user, StageContext currentStage) {
//        String userInput = user.getContent().trim();
//
//        // 🔁 사용자가 직접 초기화 요청한 경우
//        if ("처음으로".equalsIgnoreCase(userInput) || "종료".equalsIgnoreCase(userInput)) {
//            return FeatureContext.INITIAL;
//        }
//
//        // 🔀 현재 단계(stageContext)에 따라 다음 기능 결정
//        return switch (currentStage) {
//            // 초기 진입 or 기능 종료 후
//            case START, PROMPT_NEXT_ACTION -> FeatureContext.INITIAL;
//
//            // 문제 생성 흐름
//            case SELECT_TYPE, PROMPT_CHAPTER_PAGE, PROMPT_CONCEPT, GENERATING_PROBLEM ->
//                    FeatureContext.PROBLEM_GENERATION;
//
//            // 문제 풀이 흐름
//            case PROBLEM_PRESENTED, USER_ANSWER, CORRECT_FEEDBACK, INCORRECT_FEEDBACK ->
//                    FeatureContext.PROBLEM_SOLVING;
//
//            // 개념 설명 및 피드백 흐름
//            case EXPLANATION_PRESENTED, FEEDBACK_RATING, PROMPT_FEEDBACK_TEXT,
//                 INPUT_FEEDBACK_TEXT, RE_EXPLANATION_PRESENTED ->
//                    FeatureContext.CONCEPT_EXPLANATION;
//        };
//    }
//
//    /**
//     * 다음 StageContext (기능 내 단계) 계산
//     */
//    private StageContext calculateNextStageContext(AiMessageDto ai, UserMessageDto user, StageContext currentStage) {
//        String userInput = user.getContent().trim();
//
//        // 🔁 사용자 요청으로 흐름을 초기화
//        if ("처음으로".equalsIgnoreCase(userInput) || "종료".equalsIgnoreCase(userInput)) {
//            return StageContext.START;
//        }
//
//        // 🔁 현재 단계 기준으로 다음 단계 결정
//        return switch (currentStage) {
//            // 처음 진입: 기능 선택으로 유도
//            case START -> StageContext.SELECT_TYPE;
//
//            // 기능 선택지에 대한 사용자 응답
//            case SELECT_TYPE -> {
//                if ("1".equals(userInput)) yield StageContext.PROMPT_CHAPTER_PAGE;
//                else if ("2".equals(userInput)) yield StageContext.PROMPT_CONCEPT;
//                else yield StageContext.SELECT_TYPE; // 잘못된 입력 → 반복
//            }
//
//            // 입력 이후 문제 생성 요청 단계로 전이
//            case PROMPT_CHAPTER_PAGE, PROMPT_CONCEPT -> StageContext.GENERATING_PROBLEM;
//
//            // 문제 생성 완료 후 문제 제시
//            case GENERATING_PROBLEM -> StageContext.PROBLEM_PRESENTED;
//
//            // 문제 제시 후 사용자 응답 대기
//            case PROBLEM_PRESENTED -> StageContext.USER_ANSWER;
//
//            // 사용자 응답을 받았지만 계속 문제 풀이 단계 유지
//            case USER_ANSWER -> {
//                // 여기서는 AI의 답변에 따라 정답/오답 피드백으로 분기
//                // 실제로는 FastAPI에서 정답 여부를 판단해서 응답해야 함
//                yield StageContext.CORRECT_FEEDBACK; // 임시로 정답 처리
//            }
//
//            // 정답 피드백 이후 분기
//            case CORRECT_FEEDBACK -> {
//                if ("1".equals(userInput)) yield StageContext.PROBLEM_PRESENTED;
//                else yield StageContext.PROMPT_NEXT_ACTION;
//            }
//
//            // 오답 피드백 이후 분기
//            case INCORRECT_FEEDBACK -> {
//                if ("1".equals(userInput)) yield StageContext.EXPLANATION_PRESENTED;
//                else if ("2".equals(userInput)) yield StageContext.PROBLEM_PRESENTED;
//                else yield StageContext.PROMPT_NEXT_ACTION;
//            }
//
//            // 개념 설명 후 → 이해도 평가
//            case EXPLANATION_PRESENTED -> StageContext.FEEDBACK_RATING;
//
//            // 이해도 점수 평가
//            case FEEDBACK_RATING -> {
//                try {
//                    int score = Integer.parseInt(userInput);
//                    if (score >= 4) yield StageContext.PROMPT_NEXT_ACTION;
//                    else yield StageContext.PROMPT_FEEDBACK_TEXT;
//                } catch (NumberFormatException e) {
//                    yield StageContext.FEEDBACK_RATING;
//                }
//            }
//
//            // 피드백 작성 단계
//            case PROMPT_FEEDBACK_TEXT -> StageContext.INPUT_FEEDBACK_TEXT;
//
//            // 입력받은 피드백을 바탕으로 재설명
//            case INPUT_FEEDBACK_TEXT -> StageContext.RE_EXPLANATION_PRESENTED;
//
//            // 재설명 이후 다시 점수 요청
//            case RE_EXPLANATION_PRESENTED -> StageContext.FEEDBACK_RATING;
//
//            // 기능 종료 후 기능 선택 화면 복귀
//            case PROMPT_NEXT_ACTION -> StageContext.SELECT_TYPE;
//        };
//    }
}