package com.example.application.domain.chat.service;

import com.example.application.domain.chat.dto.AiMessageDto;
import com.example.application.domain.chat.dto.UserMessageDto;
import com.example.application.domain.chat.dto.request.ConceptExplanationRequestDto;
import com.example.application.domain.chat.dto.response.ChatHistoryResponseDto;
import com.example.application.domain.chat.dto.response.ConceptExplanationResponseDto;
import com.example.application.domain.chat.dto.response.GeneratingQuestionResponseDto;
import com.example.application.domain.book.entity.Book;
import com.example.application.domain.chat.entity.ChatHistory;
import com.example.application.domain.chat.type.ChatState;
import com.example.application.domain.chat.type.MessageType;
import com.example.application.domain.question.entity.Question;
import com.example.application.domain.user.entity.User;
import com.example.application.domain.book.repository.BookRepository;
import com.example.application.domain.chat.repository.ChatHistoryRepository;
import com.example.application.domain.question.repository.QuestionRepository;
import com.example.application.domain.user.repository.UserRepository;
import com.example.application.domain.chat.type.Sender;
import com.example.application.global.exception.CustomException;
import com.example.application.global.exception.ErrorCode;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
@Slf4j
public class ChatService {

    // ChatHistory의 '저장/조회'를 담당하는 서비스 (트랜잭션 분리)
    private final ChatHistoryService chatHistoryService;
    private final WebClient fastApiWebClient; // FastAPI(AI 서버) 통신용

    // ChatService가 직접 의존하는 리포지토리
    private final QuestionRepository questionRepository;
    private final UserRepository userRepository;
    private final ChatHistoryRepository chatHistoryRepository;
    private final BookRepository bookRepository;

    /**
     * 사용자의 메시지를 받아 전체 채팅 흐름을 오케스트레이션(Orchestration)합니다.
     * 1. 현재 상태(State) 판별
     * 2. 다음 상태 결정 (State Transition)
     * 3. FastAPI(AI) 호출 여부 판단
     * 4. 사용자/AI 메시지 저장 (chatHistoryService 위임)
     * 5. 후속 응답(Follow-up) 생성
     */
    public List<AiMessageDto> handleChatFlow(Long userId, UserMessageDto userMessageDto) {
        List<AiMessageDto> responses = new ArrayList<>();

        Long bookId = userMessageDto.getBookId();

        // userMessageDto에서 state가 넘어오면 해당 상태를 우선적으로 사용
        ChatState currentState = userMessageDto.getChatState();

        if (currentState == null) {
            // fallback: DB에서 마지막 상태 조회
            currentState = chatHistoryService.findLastMessage(userId, bookId)
                    .map(ChatHistoryResponseDto::getChatState)
                    .orElse(ChatState.WAITING_USER_SELECT_FEATURE);
        }

        // 빈 메시지인 경우: 초기 진입 상태만 유도, 유저 메시지는 저장 X
        if (userMessageDto.getContent() == null || userMessageDto.getContent().trim().isEmpty()) {
            ChatState initState = ChatState.WAITING_USER_SELECT_FEATURE;
            AiMessageDto initMessage = buildLocalAiMessage(userId, bookId, initState);
            initMessage.setChatState(initState);
            // AI 초기 메시지 저장
            chatHistoryService.saveAiMessage(initMessage, initState);
            responses.add(initMessage);
            return responses;
        }

        // 1. 다음 상태 전이 결정 (순수 Java 로직)
        ChatState nextState = determineNextState(currentState, userMessageDto.getContent());
        userMessageDto.setChatState(nextState);

        // 2. 상태에 따른 추가 작업 (예: 문제 답변 저장)
        if (nextState == ChatState.EVALUATING_ANSWER_AND_LOGGING) {
            updateUserAnswerToLatestQuestion(userId, bookId, userMessageDto.getContent());
        }

        // 3. FastAPI(AI) 호출 여부 판단 및 실행
        AiMessageDto aiMessageDto = shouldCallFastApi(nextState)
                ? callFastApiByState(userMessageDto)
                : buildLocalAiMessage(userId, bookId, nextState);

        // 4. 메시지 저장 (트랜잭션 위임)
        chatHistoryService.saveUserMessage(userMessageDto, currentState);
        chatHistoryService.saveAiMessage(aiMessageDto, nextState);

        responses.add(aiMessageDto);

        // 5. AI 응답 후, 사용자의 입력을 기다리는 후속 메시지(Follow-up)가 필요한 경우
        if (nextState == ChatState.EVALUATING_ANSWER_AND_LOGGING || nextState == ChatState.CONCEPT_REEXPLANATION || nextState == ChatState.PRESENTING_CONCEPT_EXPLANATION || nextState == ChatState.PROCESSING_PAGE_SEARCH_RESULT) {
            // AI 응답(nextState) 이후의 상태 결정
            ChatState afterNextState = determineNextState(nextState, userMessageDto.getContent());
            AiMessageDto followUpMessage = buildLocalAiMessage(userId, bookId, afterNextState);

            // 후속 메시지 저장
            chatHistoryService.saveAiMessage(followUpMessage, afterNextState);
            responses.add(followUpMessage);
        }

        return responses;
    }

    /**
     * 채팅 Finite State Machine (FSM)의 핵심 로직.
     * 현재 상태(currentState)와 사용자 입력(content)을 기반으로 다음 상태를 결정(전이)
     */
    private ChatState determineNextState(ChatState currentState, String content) {
        return switch (currentState) {
            // 초기 기능 선택 상태: 1. 문제 생성, 2. 페이지 찾기, 3. 개념 설명
            case WAITING_USER_SELECT_FEATURE -> switch (content) {
                case "1" -> ChatState.WAITING_PROBLEM_CRITERIA_SELECTION;
                case "2" -> ChatState.WAITING_KEYWORD_FOR_PAGE_SEARCH;
                case "3" -> ChatState.WAITING_CONCEPT_INPUT;
                default -> ChatState.WAITING_USER_SELECT_FEATURE;
            };

            // 1. 문제 생성 흐름
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
            case WAITING_REASON_FOR_LOW_RATING -> ChatState.CONCEPT_REEXPLANATION;
            case CONCEPT_REEXPLANATION -> ChatState.WAITING_CONCEPT_RATING;

            // 사용자 선택: 다음 문제 or 기능 선택으로 분기
            case WAITING_NEXT_ACTION_AFTER_LEARNING -> {
                if (content.equals("1")) yield ChatState.GENERATING_ADDITIONAL_QUESTION_WITH_RAG;
                else yield ChatState.WAITING_USER_SELECT_FEATURE;
            }

            case GENERATING_ADDITIONAL_QUESTION_WITH_RAG -> ChatState.EVALUATING_ANSWER_AND_LOGGING;


            // 2. 페이지 찾기 흐름 → 키워드 입력 받기
            case WAITING_KEYWORD_FOR_PAGE_SEARCH -> ChatState.PROCESSING_PAGE_SEARCH_RESULT;
            case PROCESSING_PAGE_SEARCH_RESULT -> ChatState.WAITING_USER_SELECT_FEATURE;


            // 3. 개념 설명 흐름 → 개념 입력 → 설명 → 평가
            case WAITING_CONCEPT_INPUT -> ChatState.PRESENTING_CONCEPT_EXPLANATION;
            case PRESENTING_CONCEPT_EXPLANATION -> ChatState.WAITING_CONCEPT_RATING;

            default -> currentState;
        };
    }

    /**
     * 현재 상태가 FastAPI(AI) 호출을 요구하는지 판단
     */
    private boolean shouldCallFastApi(ChatState state) {
        return switch (state) {
            case GENERATING_QUESTION_WITH_RAG,
                 GENERATING_ADDITIONAL_QUESTION_WITH_RAG,
                 EVALUATING_ANSWER_AND_LOGGING,
                 PRESENTING_CONCEPT_EXPLANATION,
                 CONCEPT_REEXPLANATION,
                 PROCESSING_PAGE_SEARCH_RESULT -> true;
            default -> false;
        };
    }

    /**
     * ChatState에 따라 적절한 FastAPI 엔드포인트(/uri)를 호출하는 라우터(Router) 메소드
     * 각 엔드 포인트에 맞는 DTO로 변환 후 요청
     */
    public AiMessageDto callFastApiByState(UserMessageDto userMessageDto) {
        ChatState state = userMessageDto.getChatState();
        // 1. 상태에 맞는 요청 DTO(Payload) 생성
        Object requestDto = convertToRequestDtoByState(userMessageDto);

        try {
            // 2. 상태에 맞는 URI 결정
            String uri = switch (state) {
                case GENERATING_QUESTION_WITH_RAG -> "/generating-question";
                case GENERATING_ADDITIONAL_QUESTION_WITH_RAG -> "/generating-additional-question";
                case EVALUATING_ANSWER_AND_LOGGING -> "/evaluating/answer";
                case PRESENTING_CONCEPT_EXPLANATION -> "/learning/concept-explanation";
                case CONCEPT_REEXPLANATION -> "/learning/explanation";
                case PROCESSING_PAGE_SEARCH_RESULT -> "/processing-page-search-result";
                default -> throw new IllegalArgumentException("정의되지 않은 상태: " + state);
            };

            // 3. API 호출 및 응답 처리
            return switch (state) {
                // 특정 상태는 응답 DTO가 다르므로 별도 처리
                case PRESENTING_CONCEPT_EXPLANATION, CONCEPT_REEXPLANATION -> {
                    ConceptExplanationResponseDto response = fastApiWebClient.post()
                            .uri(uri)
                            .bodyValue(requestDto)
                            .retrieve()
                            .bodyToMono(ConceptExplanationResponseDto.class)
                            .block();

                    // AiMessageDto 형태로 변환하여 반환
                    yield AiMessageDto.builder()
                            .userId(userMessageDto.getUserId())
                            .bookId(userMessageDto.getBookId())
                            .chatState(state)
                            .messageType(MessageType.TEXT)
                            .content(response.getResult().getExplanation()) // 설명 텍스트만 추출
                            .build();
                }

                case GENERATING_QUESTION_WITH_RAG, GENERATING_ADDITIONAL_QUESTION_WITH_RAG -> {
                    GeneratingQuestionResponseDto response = fastApiWebClient.post()
                            .uri(uri)
                            .bodyValue(requestDto)
                            .retrieve()
                            .bodyToMono(GeneratingQuestionResponseDto.class)
                            .block();

                    // AI가 생성한 문제를 DB(Question 테이블)에 저장
                    saveQuestionFromResponse(response);

                    yield AiMessageDto.builder()
                            .userId(userMessageDto.getUserId())
                            .bookId(userMessageDto.getBookId())
                            .chatState(state)
                            .messageType(MessageType.TEXT)
                            .content(response.getContent()) // 설명 텍스트만 추출
                            .build();
                }

                // 그 외 상태는 AiMessageDto로 바로 매핑
                default -> fastApiWebClient.post()
                        .uri(uri)
                        .bodyValue(requestDto)
                        .retrieve()
                        .bodyToMono(AiMessageDto.class)
                        .block();
            };

        } catch (Exception e) {
            log.error("FastAPI 호출 실패 (state = {})", state, e);
            return buildFastApiErrorMessage(userMessageDto);
        }
    }

    /**
     * FastAPI로 보낼 요청 DTO(Payload)를 상태(State)에 맞게 생성
     */
    private Object convertToRequestDtoByState(UserMessageDto userMessageDto) {
        ChatState state = userMessageDto.getChatState();

        return switch (state) {
            // 단순 메시지 전달
            case PRESENTING_CONCEPT_EXPLANATION, GENERATING_QUESTION_WITH_RAG, EVALUATING_ANSWER_AND_LOGGING, PROCESSING_PAGE_SEARCH_RESULT ->
                    UserMessageDto.builder()
                            .userId(userMessageDto.getUserId())
                            .bookId(userMessageDto.getBookId())
                            .content(userMessageDto.getContent())
                            .messageType(userMessageDto.getMessageType())
                            .chatState(state)
                            .build();

            // 추가 문제 생성 시, 마지막 문제의 컨텍스트를 조회하여 DTO에 포함
            case GENERATING_ADDITIONAL_QUESTION_WITH_RAG -> {
                User user = userRepository.getReferenceById(userMessageDto.getUserId());
                Book book = bookRepository.getReferenceById(userMessageDto.getBookId());

                Optional<Question> lastQuestionOptional = questionRepository.findTopByUserAndBookOrderByCreatedAtDesc(
                        user, book
                );

                String content = "Java"; // 기본값 설정
                if (lastQuestionOptional.isPresent()) {
                    Question lastQuestion = lastQuestionOptional.get();
                    if (lastQuestion.getConcept() != null && !lastQuestion.getConcept().isBlank()) {
                        content = lastQuestion.getConcept();
                    } else if (lastQuestion.getText() != null && !lastQuestion.getText().isBlank()) {
                        content = lastQuestion.getText(); // concept이 없으면 problemText를 사용
                    }
                }

                yield UserMessageDto.builder()
                        .userId(userMessageDto.getUserId())
                        .bookId(userMessageDto.getBookId())
                        .content(content) // 안전하게 확보된 content 사용
                        .messageType(userMessageDto.getMessageType())
                        .chatState(state)
                        .build();
            }

            // (재)설명에 필요한 특정 컨텍스트(사용자, 문제, 평가 이력)를 조립
            case CONCEPT_REEXPLANATION ->
                    buildConceptExplanationRequest(userMessageDto);

            default -> userMessageDto;
        };
    }

    /**
     * AI의 개념 설명/재설명(FastAPI /learning/explanation)을 위해,
     * 사용자 정보, 최근 문제 정보, 과거의 '낮은 이해도' 평가 이력을 모두 조회하여
     * 'ConceptExplanationRequestDto'를 조립
     */
    private ConceptExplanationRequestDto buildConceptExplanationRequest(UserMessageDto userMessageDto) {
        Long userId = userMessageDto.getUserId();
        Long bookId = userMessageDto.getBookId();

        // [JPA 최적화] getReferenceById: SELECT 쿼리 없이 ID만 가진 프록시(껍데기) 객체 생성
        // user와 book 프록시 객체 생성
        User user = userRepository.getReferenceById(userId);
        Book book = bookRepository.getReferenceById(bookId);

        // 1. UserInfo 조회
        User userEntity = userRepository.findById(userId)
                .orElseThrow(() -> new IllegalArgumentException("유저를 찾을 수 없습니다: " + userId));
        ConceptExplanationRequestDto.UserInfo userInfo = ConceptExplanationRequestDto.UserInfo.from(userEntity);

        // 2. ProblemInfo 조회
        Question question = questionRepository.findTopByUserAndBookOrderByCreatedAtDesc(user, book)
                .orElseThrow(() -> new IllegalStateException("최근 Question을 찾을 수 없습니다."));

        ChatHistory userAnswer = chatHistoryRepository.findTopByUserAndBookAndSenderOrderByCreatedAtDesc(
                user, book, Sender.USER).orElse(null);

        ConceptExplanationRequestDto.ProblemInfo problemInfo =
                ConceptExplanationRequestDto.ProblemInfo.from(question, userAnswer);

        // 3. LowUnderstandingAttempts(이해도 점수 낮은 데이터 리스트), BestAttempt (이해도 높은 데이터) 조회

        // DB 필터링을 통해 불필요한 전체 데이터를 조회하지 않도록 최적화한 쿼리
        List<ChatHistory> allExplanationWithRatings = chatHistoryRepository.findAiExplanationsWithRatingsByUserAndBookAndStates(
                user,
                book,
                Sender.AI,
                List.of(ChatState.PRESENTING_CONCEPT_EXPLANATION, ChatState.WAITING_CONCEPT_RATING)
        );

        // 낮은 점수 사유(피드백) 목록을 미리 한 번에 모두 조회
        List<ChatHistory> allFeedbacks = chatHistoryRepository.findAllFeedbacks(
                user,
                book,
                Sender.USER,
                ChatState.WAITING_REASON_FOR_LOW_RATING
        );

        List<ConceptExplanationRequestDto.LowUnderstandingAttempt> lowAttempts = new ArrayList<>();
        ConceptExplanationRequestDto.BestAttempt bestAttempt = null;

        // AI 설명 메시지만 필터링하여 맵 생성
        var explanationMap = allExplanationWithRatings.stream()
                .filter(ch -> ch.getChatState() == ChatState.PRESENTING_CONCEPT_EXPLANATION)
                .collect(Collectors.toMap(ChatHistory::getCreatedAt, ch -> ch));

        // 사용자 평가 메시지만 필터링하여 리스트 생성
        List<ChatHistory> ratingMessages = allExplanationWithRatings.stream()
                .filter(ch -> ch.getChatState() == ChatState.WAITING_CONCEPT_RATING)
                .toList();

        // ratingMessages 리스트를 순회
        for (ChatHistory ratingMsg : ratingMessages) {
            Integer score = parseIntOrNull(ratingMsg.getContent());
            if (score != null) {
                // 직전 AI 메시지(설명)를 맵에서 찾기
                ChatHistory prevAiMsg = explanationMap.get(ratingMsg.getCreatedAt().minusSeconds(1)); // 근사치로 탐색

                if (score >= 4 && bestAttempt == null) {
                    bestAttempt = ConceptExplanationRequestDto.BestAttempt.from(prevAiMsg, ratingMsg);
                } else if (score <= 3) {
                    ChatHistory feedback = allFeedbacks.stream()
                            .filter(fb -> fb.getCreatedAt().isAfter(ratingMsg.getCreatedAt()))
                            .findFirst()
                            .orElse(null);

                    // (성능 최적화) 찾은 feedback은 리스트에서 제거하여 중복 검색 방지
                    if (feedback != null) {
                        allFeedbacks.remove(feedback);
                    }

                    lowAttempts.add(ConceptExplanationRequestDto.LowUnderstandingAttempt.from(prevAiMsg, ratingMsg, feedback));
                }
            }
        }

        // 4. 최종 객체 조립
        return ConceptExplanationRequestDto.builder()
                .userInfo(userInfo)
                .problemInfo(problemInfo)
                .lowUnderstandingAttempts(lowAttempts)
                .bestAttempt(bestAttempt)
                .build();
    }

    private static Integer parseIntOrNull(String s) {
        try {
            return s == null ? null : Integer.parseInt(s.trim());
        } catch (NumberFormatException e) {
            return null;
        }
    }

    /**
     * AI 응답(문제 생성)을 DB Question 테이블에 저장
     * [JPA 최적화] 'getReferenceById'를 사용해 User, Book 엔티티를 SELECT하지 않고
     * INSERT 쿼리만 실행
     */
    private void saveQuestionFromResponse(GeneratingQuestionResponseDto response) {
        User user = userRepository.getReferenceById(response.getUserId());
        Book book = bookRepository.getReferenceById(response.getBookId());

        Question question = Question.builder()
                .user(user)
                .book(book)
                .domain(response.getDomain())
                .concept(response.getConcept())
                .text(response.getProblemText())
                .userAnswer(null) // 사용자가 답변하면 이후 업데이트 가능
                .correctAnswer(response.getCorrectAnswer())
                .build();

        questionRepository.save(question);
    }

    /**
     * 사용자의 답변(content)을 가장 최근의 Question 레코드에 업데이트
     */
    private void updateUserAnswerToLatestQuestion(Long userId, Long bookId, String userAnswer) {
        User user = userRepository.getReferenceById(userId);
        Book book = bookRepository.getReferenceById(bookId);

        questionRepository.findTopByUserAndBookOrderByCreatedAtDesc(user, book)
                .ifPresent(question -> {
                    question.setUserAnswer(userAnswer);
                    questionRepository.save(question);
                });
    }

    /**
     * FastAPI(AI) 호출이 필요 없는,
     * 미리 정의된 로컬 응답 메시지를 생성
     */
    private AiMessageDto buildLocalAiMessage(Long userId, Long bookId, ChatState state) {
        String message = switch (state) {
            case WAITING_USER_SELECT_FEATURE -> """
                    👋 안녕하세요! 어떤 걸 도와드릴까요?
                    
                    1️⃣ 예상 문제 생성  
                    2️⃣ 페이지 찾기  
                    3️⃣ 개념 설명
                    """;

            case WAITING_PROBLEM_CRITERIA_SELECTION -> """
                    🧠 문제를 어떤 기준으로 생성할까요?
                    
                    1️⃣ 챕터나 페이지 범위  
                    2️⃣ 특정 개념
                    """;

            case WAITING_PROBLEM_CONTEXT_INPUT -> """
                    ✏️ 문제 생성을 위한 챕터나 페이지 범위를 입력해주세요.
                    
                    예시  
                    - '3장 전체'  
                    - '10 ~ 15페이지'
                    """;

            case WAITING_CONCEPT_INPUT -> """
                    📘 어떤 개념을 설명해드릴까요?
                    
                    예시  
                    - '데드락'  
                    - 'DFS와 BFS의 차이점'
                    """;

            case WAITING_KEYWORD_FOR_PAGE_SEARCH -> """
                    🔍 찾고 싶은 내용을 입력해주세요.
                    
                    예시  
                    - 'OSI 7계층'  
                    - '힙 정렬 예제'
                    """;

            case WAITING_NEXT_ACTION_AFTER_LEARNING -> """
                    ✅ 다음으로 무엇을 할까요?
                    
                    1️⃣ 다음 문제 풀기  
                    2️⃣ 다른 기능 선택
                    """;

            case WAITING_CONCEPT_RATING -> """
                    ⭐ 설명이 얼마나 도움이 되었나요?
                    
                    1점 (전혀 이해 안 됨) ~ 5점 (매우 도움 됨) 중 숫자로 평가해주세요.
                    """;

            case WAITING_REASON_FOR_LOW_RATING -> """
                    🤔 이해가 어려웠던 점을 알려주세요!
                    
                    어떤 부분이 헷갈렸는지 알려주시면 더 쉽게 다시 설명드릴게요.
                    """;

            default -> """
                    ✅ 입력을 확인했어요.  
                    다음 단계로 넘어갈게요!
                    """;
        };

        return AiMessageDto.builder()
                .userId(userId)
                .bookId(bookId)
                .content(message)
                .messageType(MessageType.TEXT)
                .chatState(state)
                .build();
    }

    /**
     * FastAPI 호출 실패 시 사용자에게 보여줄 표준 에러 메시지를 생성
     */
    private AiMessageDto buildFastApiErrorMessage(UserMessageDto dto) {
        return AiMessageDto.builder()
                .userId(dto.getUserId())
                .bookId(dto.getBookId())
                .content("⚠️ FastAPI 응답에 실패했습니다. 다시 시도해주세요.")
                .chatState(dto.getChatState())
                .messageType(MessageType.TEXT)
                .build();
    }

    /**
     * (헬스 체크용) FastAPI 서버 연결 상태를 확인
     */
    public void checkFastApiConnection() {
        try {
            fastApiWebClient.get()
                    .uri("/ping")
                    .retrieve()
                    .toBodilessEntity()
                    .block();
        } catch (Exception e) {
            log.error("AI Server (FastAPI) 연결 실패: {}", e.getMessage());
            throw new CustomException(ErrorCode.AI_SERVER_UNAVAILABLE);
        }
    }
}