package com.example.application.dto.chat;

import com.example.application.entity.ChatHistory.FeatureContext;
import com.example.application.entity.ChatHistory.StageContext;
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
    private String userId;
    private Long bookId;
    @Builder.Default
    private String sender = "USER";
    private String content;
    private String messageType; // TEXT, SELECTION, RATING 등

    private FeatureContext featureContext;
    private StageContext stageContext;
}