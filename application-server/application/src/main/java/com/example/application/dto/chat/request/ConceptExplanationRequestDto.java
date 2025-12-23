package com.example.application.dto.chat.request;

import com.example.application.entity.ChatHistory;
import com.example.application.entity.Question;
import com.example.application.entity.User;
import com.fasterxml.jackson.databind.PropertyNamingStrategies;
import com.fasterxml.jackson.databind.annotation.JsonNaming;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;

import java.time.LocalDate;
import java.util.List;

@Getter
@Builder
@AllArgsConstructor
@JsonNaming(PropertyNamingStrategies.SnakeCaseStrategy.class)
public class ConceptExplanationRequestDto {

    private UserInfo userInfo;
    private ProblemInfo problemInfo;
    private List<LowUnderstandingAttempt> lowUnderstandingAttempts;
    private BestAttempt bestAttempt;

    @Getter
    @Builder
    @AllArgsConstructor
    @JsonNaming(PropertyNamingStrategies.SnakeCaseStrategy.class)
    public static class UserInfo {
        private Long userId;
        private Integer age;
        private String learningExperience;

        public static UserInfo from(User user) {
            return UserInfo.builder()
                    .userId(user.getUserId())
                    .age(user.getBirthDate() == null ? null
                            : LocalDate.now().getYear() - user.getBirthDate().getYear())
                    .learningExperience(user.getJob())
                    .build();
        }
    }

    @Getter
    @Builder
    @AllArgsConstructor
    @JsonNaming(PropertyNamingStrategies.SnakeCaseStrategy.class)
    public static class ProblemInfo {
        private String domain;
        private String concept;
        private String problemText;
        private String userAnswer;
        private String correctAnswer;

        public static ProblemInfo from(Question q, ChatHistory userAnswerMsg) {
            return ProblemInfo.builder()
                    .domain(q.getDomain())
                    .concept(q.getConcept())
                    .problemText(q.getText())
                    .userAnswer(userAnswerMsg != null ? userAnswerMsg.getContent() : null)
                    .correctAnswer(q.getCorrectAnswer())
                    .build();
        }
    }

    @Getter
    @Builder
    @AllArgsConstructor
    @JsonNaming(PropertyNamingStrategies.SnakeCaseStrategy.class)
    public static class LowUnderstandingAttempt {
        private String explanationText;
        private String feedbackText;
        private Integer understandingScore;

        public static LowUnderstandingAttempt from(ChatHistory aiMsg, ChatHistory rating, ChatHistory feedback) {
            Integer score = null;
            if (rating != null && rating.getContent() != null) {
                try {
                    score = Integer.parseInt(rating.getContent().trim());
                } catch (NumberFormatException e) {
                    // 숫자로 변환 실패 시 score는 null 유지
                }
            }

            return LowUnderstandingAttempt.builder()
                    .explanationText(aiMsg.getContent())
                    .feedbackText(feedback != null ? feedback.getContent() : null)
                    .understandingScore(score)
                    .build();
        }
    }

    @Getter
    @Builder
    @AllArgsConstructor
    @JsonNaming(PropertyNamingStrategies.SnakeCaseStrategy.class)
    public static class BestAttempt {
        private String explanationText;
        private Integer understandingScore;

        public static BestAttempt from(ChatHistory aiMsg, ChatHistory rating) {
            Integer score = null;
            if (rating != null && rating.getContent() != null) {
                try {
                    score = Integer.parseInt(rating.getContent().trim());
                } catch (NumberFormatException e) {
                    // 숫자로 변환 실패 시 score는 null 유지
                }
            }

            return BestAttempt.builder()
                    .explanationText(aiMsg.getContent())
                    .understandingScore(score)
                    .build();
        }
    }
}

