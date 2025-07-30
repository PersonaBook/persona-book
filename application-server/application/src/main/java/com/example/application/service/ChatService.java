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
        String content = userMessageDto.getContent();

        log.info("=== ChatService Debug ===");
        log.info("userId: {}", userId);
        log.info("bookId: {}", bookId);
        log.info("content: '{}'", content);
        log.info("chatState: {}", userMessageDto.getChatState());

        // userMessageDto에서 state가 넘어오면 그걸 우선 사용 (프론트에서 새로운 대화를 위해 WAITING_USER_SELECT_FEATURE를 보내는 경우가 있음)
        ChatState currentState = userMessageDto.getChatState();

        if (currentState == null) {
            // fallback: DB에서 마지막 상태 조회
            currentState = chatHistoryService.findLastMessage(userId, bookId)
                    .map(ChatHistory::getChatState)
                    .orElse(ChatState.WAITING_USER_SELECT_FEATURE);
        }
        
        log.info("currentState: {}", currentState);

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
        
        // FastAPI 호출 여부 판단 (다음 상태 기준)
        log.info("🔍 handleChatFlow - currentState: {}, nextState: {}", currentState, nextState);
        log.info("🔍 handleChatFlow - shouldCallFastApi 호출 전");
        boolean shouldCall = shouldCallFastApi(nextState);
        log.info("🔍 handleChatFlow - shouldCall: {}", shouldCall);
        
        log.info("🔍 handleChatFlow - shouldCall이 true인지 확인: {}", shouldCall);
        
        AiMessageDto aiMessageDto;
        if (shouldCall) {
            log.info("🔍 handleChatFlow - callFastApi 호출");
            aiMessageDto = callFastApi(userMessageDto);
        } else {
            log.info("🔍 handleChatFlow - buildLocalAiMessage 호출");
            aiMessageDto = buildLocalAiMessage(nextState, userId, bookId);
        }

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
        log.info("determineNextState - currentState: {}, content: '{}'", currentState, content);
        
        ChatState nextState = switch (currentState) {
            // 초기 기능 선택 상태: 1. 문제 생성, 2. 페이지 찾기, 3. 개념 설명
            case WAITING_USER_SELECT_FEATURE -> switch (content) {
                case "1" -> ChatState.WAITING_PROBLEM_CRITERIA_SELECTION;
                case "2" -> ChatState.WAITING_KEYWORD_FOR_PAGE_SEARCH;
                case "3" -> ChatState.WAITING_CONCEPT_INPUT;
                default -> ChatState.WAITING_USER_SELECT_FEATURE;
            };

            // ✅ 1. 문제 생성 흐름
            case WAITING_PROBLEM_CRITERIA_SELECTION -> ChatState.WAITING_PROBLEM_CONTEXT_INPUT; // 챕터/개념 입력 요청
            case WAITING_PROBLEM_CONTEXT_INPUT -> {
                // 사용자가 실제 입력을 했을 때만 문제 생성 시작
                if (content != null && !content.trim().isEmpty()) {
                    yield ChatState.GENERATING_QUESTION_WITH_RAG; // 입력 기반 RAG 생성 요청
                } else {
                    yield ChatState.WAITING_PROBLEM_CONTEXT_INPUT; // 입력 대기
                }
            }

            case GENERATING_QUESTION_WITH_RAG -> ChatState.WAITING_USER_ANSWER; // 문제 제시 완료, 답 대기

            // 사용자 답 입력 → 정답/오답 판단
            case WAITING_USER_ANSWER -> ChatState.EVALUATING_ANSWER_AND_LOGGING;

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
        
        log.info("determineNextState - nextState: {}", nextState);
        return nextState;
    }

    private boolean shouldCallFastApi(ChatState state) {
        boolean shouldCall = switch (state) {
            case GENERATING_QUESTION_WITH_RAG,
                 GENERATING_ADDITIONAL_QUESTION_WITH_RAG,
                 EVALUATING_ANSWER_AND_LOGGING,
                 PRESENTING_CONCEPT_EXPLANATION,
                 REEXPLAINING_CONCEPT,
                 PROCESSING_PAGE_SEARCH_RESULT -> true;
            default -> false;
        };
        
        log.info("🔍 shouldCallFastApi - state: {}, shouldCall: {}", state, shouldCall);
        return shouldCall;
    }

    // ChatState에 따라 다른 엔드 포인트로 FastAPI 호출할 수 있도록 로직 바꾸어야 함
    private AiMessageDto callFastApi(UserMessageDto dto) {
        log.info("🚀 FastAPI 호출 시작");
        log.info("📊 요청 데이터: userId={}, bookId={}, content='{}', chatState={}", 
                dto.getUserId(), dto.getBookId(), dto.getContent(), dto.getChatState());
        
        // ChatState에 따라 다른 엔드포인트 호출
        String endpoint = switch (dto.getChatState()) {
            case GENERATING_QUESTION_WITH_RAG -> "/chat";
            case GENERATING_ADDITIONAL_QUESTION_WITH_RAG -> "/chat";
            case EVALUATING_ANSWER_AND_LOGGING -> "/chat";
            case PRESENTING_CONCEPT_EXPLANATION -> "/chat";
            case REEXPLAINING_CONCEPT -> "/chat";
            case PROCESSING_PAGE_SEARCH_RESULT -> "/chat";
            default -> "/chat";
        };
        
        log.info("🎯 호출할 엔드포인트: {}", endpoint);
        
        return webClient.post()
                .uri(endpoint)
                .bodyValue(dto)
                .retrieve()
                .bodyToMono(AiMessageDto.class)
                .onErrorResume(e -> {
                    log.error("FastAPI 호출 실패", e);
                    return Mono.just(buildErrorMessage(dto));
                })
                .doOnSuccess(response -> {
                    log.info("✅ FastAPI 응답 성공: {}", response.getContent());
                })
                .doOnError(error -> {
                    log.error("❌ FastAPI 호출 오류: {}", error.getMessage());
                })
                .block();
    }

    private AiMessageDto buildLocalAiMessage(ChatState state, Long userId, Long bookId) {
        String message = switch (state) {
            case WAITING_USER_SELECT_FEATURE -> "무엇을 도와드릴까요?\n1. 예상 문제 생성\n2. 페이지 찾기\n3. 개념 설명";
            case WAITING_PROBLEM_CRITERIA_SELECTION -> "문제를 어떤 기준으로 생성할까요?\n1. 챕터/페이지 범위\n2. 특정 개념";
            case WAITING_PROBLEM_CONTEXT_INPUT -> "문제 생성을 위한 범위나 개념을 입력해주세요.";
            case WAITING_USER_ANSWER -> "위 문제의 답을 입력해주세요.";

            case WAITING_KEYWORD_FOR_PAGE_SEARCH -> "페이지를 찾기 위한 키워드를 입력해주세요.";

            case WAITING_NEXT_ACTION_AFTER_LEARNING -> "다음으로 무엇을 하시겠습니까?\n1. 다음 문제\n2. 기능 선택";
            case WAITING_CONCEPT_RATING -> "설명이 도움이 되었나요? 1~5점으로 평가해주세요.";
            case WAITING_REASON_FOR_LOW_RATING -> "이해가 어려웠던 점을 알려주세요. 보충 설명을 드릴게요.";

            case WAITING_CONCEPT_INPUT -> "어떤 개념에 대한 설명이 필요한가요?";

            default -> "입력을 확인했습니다. 다음 단계를 진행해주세요.";
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