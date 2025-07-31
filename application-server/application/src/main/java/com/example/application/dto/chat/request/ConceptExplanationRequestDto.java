package com.example.application.dto.chat.request;

import com.example.application.entity.ChatHistory;
import com.example.application.entity.Question;
import com.example.application.entity.User;
import com.example.application.repository.ChatHistoryRepository;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import com.fasterxml.jackson.databind.PropertyNamingStrategies;
import com.fasterxml.jackson.databind.annotation.JsonNaming;
import lombok.NoArgsConstructor;

import java.time.LocalDate;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.Objects;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@JsonNaming(PropertyNamingStrategies.SnakeCaseStrategy.class)
public class ConceptExplanationRequestDto {

    private UserInfo userInfo;
    private List<LowUnderstandingAttempt> lowUnderstandingAttempts;
    private BestAttempt bestAttempt;
    private ProblemInfo problemInfo;

    // ────────────────────────────────
    // 1. 사용자 정보
    // ────────────────────────────────
    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class UserInfo {
        private Long userId;
        private Integer age;
        private String learningExperience;

        public static UserInfo from(User user) {
            return UserInfo.builder()
                    .userId(user.getUserId())
                    .age(calculateAge(user.getUserBirthDate()))
                    .learningExperience(user.getUserJob()) // 직업 → 학습 경험으로 사용
                    .build();
        }

        private static Integer calculateAge(LocalDate birthDate) {
            if (birthDate == null) return null;
            return LocalDate.now().getYear() - birthDate.getYear();
        }
    }

    // ────────────────────────────────
    // 2. 문제 정보
    // ────────────────────────────────
    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class ProblemInfo {
        private String domain;
        private String concept;
        private String problemText;
        private String userAnswer;
        private String correctAnswer;

        public static ProblemInfo from(Question question, ChatHistory userAnswerMessage) {
            return ProblemInfo.builder()
                    .domain(question.getDomain())
                    .concept(question.getConcept())
                    .problemText(question.getProblemText())
                    .userAnswer(userAnswerMessage != null ? userAnswerMessage.getContent() : null)
                    .correctAnswer(question.getCorrectAnswer())
                    .build();
        }
    }

    // ────────────────────────────────
    // 3. 낮은 이해도 시도들
    // ────────────────────────────────
    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class LowUnderstandingAttempt {
        private String explanationText;
        private String feedbackText;
        private Integer understandingScore;

        public static LowUnderstandingAttempt from(ChatHistory aiMessage, ChatHistory userRating, ChatHistory userFeedback) {
            return LowUnderstandingAttempt.builder()
                    .explanationText(aiMessage.getContent())
                    .feedbackText(userFeedback != null ? userFeedback.getContent() : null)
                    .understandingScore(userRating != null ? parseInteger(userRating.getContent()) : null)
                    .build();
        }

        public static List<LowUnderstandingAttempt> fromAll(
                Long userId,
                Long bookId,
                List<ChatHistory> aiMessages,
                ChatHistoryRepository repo
        ) {
            List<LowUnderstandingAttempt> result = new ArrayList<>();

            for (ChatHistory aiMsg : aiMessages) {
                ChatHistory rating = repo.findTopByUserIdAndBookIdAndSenderAndCreatedAtAfterAndChatState(
                        userId, bookId, ChatHistory.Sender.USER, aiMsg.getCreatedAt(), ChatHistory.ChatState.WAITING_CONCEPT_RATING
                ).orElse(null);

                Integer score = rating != null ? parseInteger(rating.getContent()) : null;
                if (score != null && score <= 3) {
                    ChatHistory feedback = repo.findTopByUserIdAndBookIdAndSenderAndCreatedAtAfterAndChatState(
                            userId, bookId, ChatHistory.Sender.USER, rating.getCreatedAt(), ChatHistory.ChatState.WAITING_REASON_FOR_LOW_RATING
                    ).orElse(null);

                    result.add(from(aiMsg, rating, feedback));
                }
            }

            return result;
        }

        private static Integer parseInteger(String content) {
            try {
                return Integer.parseInt(content.trim());
            } catch (NumberFormatException e) {
                return null;
            }
        }
    }

    // ────────────────────────────────
    // 4. 가장 높은 이해도 시도
    // ────────────────────────────────
    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class BestAttempt {
        private String explanationText;
        private Integer understandingScore;

        public static BestAttempt from(ChatHistory aiMessage, ChatHistory userRating) {
            return BestAttempt.builder()
                    .explanationText(aiMessage.getContent())
                    .understandingScore(userRating != null ? parseInteger(userRating.getContent()) : null)
                    .build();
        }

        public static BestAttempt from(
                Long userId,
                Long bookId,
                List<ChatHistory> aiMessages,
                ChatHistoryRepository repo
        ) {
            return aiMessages.stream()
                    .sorted(Comparator.comparing(ChatHistory::getCreatedAt).reversed())
                    .map(aiMsg -> {
                        ChatHistory rating = repo.findTopByUserIdAndBookIdAndSenderAndCreatedAtAfterAndChatState(
                                userId, bookId, ChatHistory.Sender.USER, aiMsg.getCreatedAt(), ChatHistory.ChatState.WAITING_CONCEPT_RATING
                        ).orElse(null);

                        Integer score = rating != null ? parseInteger(rating.getContent()) : null;
                        if (score != null && score >= 4) {
                            return from(aiMsg, rating);
                        }
                        return null;
                    })
                    .filter(Objects::nonNull)
                    .findFirst()
                    .orElse(null);
        }

        private static Integer parseInteger(String content) {
            try {
                return Integer.parseInt(content.trim());
            } catch (NumberFormatException e) {
                return null;
            }
        }
    }
}
