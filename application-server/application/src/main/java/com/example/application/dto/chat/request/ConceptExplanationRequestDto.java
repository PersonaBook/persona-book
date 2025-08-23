package com.example.application.dto.chat.request;

import com.example.application.entity.ChatHistory;
import com.example.application.entity.Question;
import com.example.application.entity.User;
import com.fasterxml.jackson.databind.PropertyNamingStrategies;
import com.fasterxml.jackson.databind.annotation.JsonNaming;
import lombok.*;

import java.time.LocalDate;
import java.util.List;

@Getter @Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
@JsonNaming(PropertyNamingStrategies.SnakeCaseStrategy.class)
public class ConceptExplanationRequestDto {

    private UserInfo userInfo;
    private List<LowUnderstandingAttempt> lowUnderstandingAttempts;
    private BestAttempt bestAttempt;
    private ProblemInfo problemInfo;

    @Getter @Setter @NoArgsConstructor @AllArgsConstructor @Builder
    @JsonNaming(PropertyNamingStrategies.SnakeCaseStrategy.class)
    public static class UserInfo {
        private Long userId;
        private Integer age;
        private String learningExperience;

        public static UserInfo from(User user) {
            return UserInfo.builder()
                    .userId(user.getUserId())
                    .age(user.getUserBirthDate() == null ? null
                            : LocalDate.now().getYear() - user.getUserBirthDate().getYear())
                    .learningExperience(user.getUserJob())
                    .build();
        }
    }

    @Getter @Setter @NoArgsConstructor @AllArgsConstructor @Builder
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
                    .problemText(q.getQuestionText())
                    .userAnswer(userAnswerMsg != null ? userAnswerMsg.getContent() : null)
                    .correctAnswer(q.getCorrectAnswer())
                    .build();
        }
    }

    @Getter @Setter @NoArgsConstructor @AllArgsConstructor @Builder
    @JsonNaming(PropertyNamingStrategies.SnakeCaseStrategy.class)
    public static class LowUnderstandingAttempt {
        private String explanationText;
        private String feedbackText;
        private Integer understandingScore;

        public static LowUnderstandingAttempt from(ChatHistory aiMsg, ChatHistory rating, ChatHistory feedback) {
            return LowUnderstandingAttempt.builder()
                    .explanationText(aiMsg.getContent())
                    .feedbackText(feedback != null ? feedback.getContent() : null)
                    .understandingScore(parseIntOrNull(rating != null ? rating.getContent() : null))
                    .build();
        }
    }

    @Getter @Setter @NoArgsConstructor @AllArgsConstructor @Builder
    @JsonNaming(PropertyNamingStrategies.SnakeCaseStrategy.class)
    public static class BestAttempt {
        private String explanationText;
        private Integer understandingScore;

        public static BestAttempt from(ChatHistory aiMsg, ChatHistory rating) {
            return BestAttempt.builder()
                    .explanationText(aiMsg.getContent())
                    .understandingScore(parseIntOrNull(rating != null ? rating.getContent() : null))
                    .build();
        }
    }

    private static Integer parseIntOrNull(String s) {
        try { return s == null ? null : Integer.parseInt(s.trim()); }
        catch (NumberFormatException e) { return null; }
    }
}

