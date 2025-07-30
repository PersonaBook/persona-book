package com.example.application.dto.chat;

import com.example.application.entity.ChatHistory.ChatState;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

// 사용자 → 서버 전송용
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class UserMessageDto {
    private Long userId;
    private Long bookId;
    @Builder.Default
    private String sender = "USER";
    private String content;
    @Builder.Default
    private String messageType = "TEXT"; // TEXT, SELECTION, RATING 등

    private ChatState chatState;
//
//    private Integer ratingScore; // 1~5점 (평가 점수, 선택적)
//    private String associatedConcept; // 관련 키워드 (선택적, question 테이블의 concept 컬럼과 역할이 겹칠 수 있음)
}