package com.example.application.service;

import com.example.application.dto.chat.AiMessageDto;
import com.example.application.dto.chat.UserMessageDto;
import com.example.application.entity.ChatHistory;
import com.example.application.entity.ChatHistory.ChatState;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.core.publisher.Mono;

import java.util.ArrayList;
import java.util.List;

@Service
@RequiredArgsConstructor
@Slf4j
public class ChatService {

    private final ChatHistoryService chatHistoryService;
    private final WebClient webClient;

    public List<AiMessageDto> handleChatFlow(UserMessageDto userMessageDto) {
        List<AiMessageDto> responses = new ArrayList<>();

        Long userId = userMessageDto.getUserId();
        Long bookId = userMessageDto.getBookId();

        // userMessageDto에서 state가 넘어오면 그걸 우선 사용 (프론트에서 새로운 대화를 위해 WAITING_USER_SELECT_FEATURE를 보내는 경우가 있음)
        ChatState currentState = userMessageDto.getChatState();

        if (currentState == null) {
            // fallback: DB에서 마지막 상태 조회
            currentState = chatHistoryService.findLastMessage(userId, bookId)
                    .map(ChatHistory::getChatState)
                    .orElse(ChatState.WAITING_USER_SELECT_FEATURE);
        }

        // 빈 메시지인 경우: 초기 진입 상태만 유도, 유저 메시지는 저장 X
        if (userMessageDto.getContent() == null || userMessageDto.getContent().trim().isEmpty()) {
            ChatState next = ChatState.WAITING_USER_SELECT_FEATURE;
            AiMessageDto initial = buildLocalAiMessage(next, userId, bookId);
            initial.setChatState(next);
            chatHistoryService.saveAiMessage(initial, userId, bookId);
            responses.add(initial);
            return responses;
        }

        // 다음 상태 전이 결정
        ChatState nextState = determineNextState(currentState, userMessageDto.getContent());
        userMessageDto.setChatState(nextState);

        // FastAPI 호출 여부 판단
        AiMessageDto aiMessageDto = shouldCallFastApi(nextState)
                ? callFastApi(userMessageDto)
                : buildLocalAiMessage(nextState, userId, bookId);

        // 다음 상태 설정 및 저장
        aiMessageDto.setChatState(nextState);
        chatHistoryService.saveUserMessage(userMessageDto, currentState);
        chatHistoryService.saveAiMessage(aiMessageDto, userId, bookId);

        responses.add(aiMessageDto);

        // ✅ 추가 처리: EVALUATING_ANSWER_AND_LOGGING 후 자동 전이
        // 추가 메시지 생성 (예: WAITING_CONCEPT_RATING)
        if (nextState == ChatState.EVALUATING_ANSWER_AND_LOGGING || nextState == ChatState.REEXPLAINING_CONCEPT) {
            ChatState nextAfterEvaluation = determineNextState(nextState, userMessageDto.getContent());
            AiMessageDto followUpMessage = buildLocalAiMessage(nextAfterEvaluation, userId, bookId);
            followUpMessage.setChatState(nextAfterEvaluation);
            chatHistoryService.saveAiMessage(followUpMessage, userId, bookId);
            responses.add(followUpMessage);
        }

        return responses;
    }

    private ChatState determineNextState(ChatState currentState, String content) {
        return switch (currentState) {
            // 초기 기능 선택 상태: 1. 문제 생성, 2. 페이지 찾기, 3. 개념 설명
            case WAITING_USER_SELECT_FEATURE -> switch (content) {
                case "1" -> ChatState.WAITING_PROBLEM_CRITERIA_SELECTION;
                case "2" -> ChatState.WAITING_KEYWORD_FOR_PAGE_SEARCH;
                case "3" -> ChatState.WAITING_CONCEPT_INPUT;
                default -> ChatState.WAITING_USER_SELECT_FEATURE;
            };

            // ✅ 1. 문제 생성 흐름
            case WAITING_PROBLEM_CRITERIA_SELECTION -> ChatState.WAITING_PROBLEM_CONTEXT_INPUT; // 챕터/개념 입력 요청
            case WAITING_PROBLEM_CONTEXT_INPUT -> ChatState.GENERATING_QUESTION_WITH_RAG; // 입력 기반 RAG 생성 요청

            case GENERATING_QUESTION_WITH_RAG -> ChatState.EVALUATING_ANSWER_AND_LOGGING; // 문제 제시 완료

            // FastAPI가 해설을 포함한 피드백 응답 → 사용자에게 바로 평가 요청
            case EVALUATING_ANSWER_AND_LOGGING -> ChatState.WAITING_CONCEPT_RATING;

            // 사용자 이해도 평가 → 점수에 따라 분기
            case WAITING_CONCEPT_RATING -> {
                try {
                    int score = Integer.parseInt(content.trim());
                    if (score >= 4) yield ChatState.WAITING_NEXT_ACTION_AFTER_LEARNING;
                    else yield ChatState.WAITING_REASON_FOR_LOW_RATING;
                } catch (NumberFormatException e) {
                    yield ChatState.WAITING_CONCEPT_RATING;
                }
            }

            // 낮은 점수 → 이유 입력 → 재설명 후 다시 평가 루프
            case WAITING_REASON_FOR_LOW_RATING -> ChatState.REEXPLAINING_CONCEPT;
            case REEXPLAINING_CONCEPT -> ChatState.WAITING_CONCEPT_RATING;

            // 사용자 선택: 다음 문제 or 기능 선택으로 분기
            case WAITING_NEXT_ACTION_AFTER_LEARNING -> {
                if (content.equals("1")) yield ChatState.GENERATING_ADDITIONAL_QUESTION_WITH_RAG;
                else yield ChatState.WAITING_USER_SELECT_FEATURE;
            }

            case GENERATING_ADDITIONAL_QUESTION_WITH_RAG -> ChatState.EVALUATING_ANSWER_AND_LOGGING;


            // ✅ 2. 페이지 찾기 흐름 → 키워드 입력 받기
            case WAITING_KEYWORD_FOR_PAGE_SEARCH -> ChatState.PROCESSING_PAGE_SEARCH_RESULT;
            case PROCESSING_PAGE_SEARCH_RESULT -> ChatState.WAITING_USER_SELECT_FEATURE;


            // ✅ 3. 개념 설명 흐름 → 개념 입력 → 설명 → 평가
            case WAITING_CONCEPT_INPUT -> ChatState.PRESENTING_CONCEPT_EXPLANATION;
            case PRESENTING_CONCEPT_EXPLANATION -> ChatState.WAITING_CONCEPT_RATING;

            default -> currentState;
        };
    }

    private boolean shouldCallFastApi(ChatState state) {
        return switch (state) {
            case GENERATING_QUESTION_WITH_RAG,
                 GENERATING_ADDITIONAL_QUESTION_WITH_RAG,
                 EVALUATING_ANSWER_AND_LOGGING,
                 PRESENTING_CONCEPT_EXPLANATION,
                 REEXPLAINING_CONCEPT,
                 PROCESSING_PAGE_SEARCH_RESULT -> true;
            default -> false;
        };
    }

    // ChatState에 따라 다른 엔드 포인트로 FastAPI 호출할 수 있도록 로직 바꾸어야 함
    private AiMessageDto callFastApi(UserMessageDto dto) {
        return webClient.post()
                .uri("/chat")
                .bodyValue(dto)
                .retrieve()
                .bodyToMono(AiMessageDto.class)
                .onErrorResume(e -> {
                    log.error("FastAPI 호출 실패", e);
                    return Mono.just(buildErrorMessage(dto));
                })
                .block();
    }

    private AiMessageDto buildLocalAiMessage(ChatState state, Long userId, Long bookId) {
        String message = switch (state) {
            case WAITING_USER_SELECT_FEATURE ->
                    """
                    👋 안녕하세요! 어떤 걸 도와드릴까요?
            
                    1️⃣ 예상 문제 생성  
                    2️⃣ 페이지 찾기  
                    3️⃣ 개념 설명
                    """;

            case WAITING_PROBLEM_CRITERIA_SELECTION ->
                    """
                    🧠 문제를 어떤 기준으로 생성할까요?
            
                    1️⃣ 챕터나 페이지 범위  
                    2️⃣ 특정 개념
                    """;

            case WAITING_PROBLEM_CONTEXT_INPUT ->
                    """
                    ✏️ 문제 생성을 위한 범위나 개념을 입력해주세요.
            
                    예시  
                    - '2장 3절'  
                    - '운영체제의 스케줄링 알고리즘'
                    """;

            case WAITING_KEYWORD_FOR_PAGE_SEARCH ->
                    """
                    🔍 찾고 싶은 내용을 입력해주세요.
            
                    예시  
                    - 'OSI 7계층'  
                    - '힙 정렬 예제'
                    """;

            case WAITING_NEXT_ACTION_AFTER_LEARNING ->
                    """
                    ✅ 다음으로 무엇을 할까요?
            
                    1️⃣ 다음 문제 풀기  
                    2️⃣ 다른 기능 선택
                    """;

            case WAITING_CONCEPT_RATING ->
                    """
                    ⭐ 설명이 얼마나 도움이 되었나요?
            
                    1점 (전혀 이해 안 됨) ~ 5점 (매우 도움 됨) 중 숫자로 평가해주세요.
                    """;

            case WAITING_REASON_FOR_LOW_RATING ->
                    """
                    🤔 이해가 어려웠던 점을 알려주세요!
            
                    어떤 부분이 헷갈렸는지 알려주시면 더 쉽게 다시 설명드릴게요.
                    """;

            case WAITING_CONCEPT_INPUT ->
                    """
                    📘 어떤 개념을 설명해드릴까요?
            
                    예시  
                    - '데드락'  
                    - 'DFS와 BFS의 차이점'
                    """;

            default ->
                    """
                    ✅ 입력을 확인했어요.  
                    다음 단계로 넘어갈게요!
                    """;
        };

        // 상태에 따라서 message를 다르게 설정해주어야 함(현재는 똑같이 설정되어 있음)
        return AiMessageDto.builder()
                .userId(userId)
                .bookId(bookId)
                .content(message)
                .messageType("TEXT")
                .chatState(state)
                .build();
    }

    private AiMessageDto buildErrorMessage(UserMessageDto dto) {
        return AiMessageDto.builder()
                .userId(dto.getUserId())
                .bookId(dto.getBookId())
                .content("⚠️ FastAPI 응답에 실패했습니다. 다시 시도해주세요.")
                .chatState(dto.getChatState())
                .messageType("TEXT")
                .build();
    }

    public boolean checkLangChainConnection() {
        try {
            return webClient.get()
                    .uri("/ping")
                    .retrieve()
                    .toBodilessEntity()
                    .block()
                    .getStatusCode()
                    .is2xxSuccessful();
        } catch (Exception e) {
            log.error("LangChain 연결 실패", e);
            return false;
        }
    }
}