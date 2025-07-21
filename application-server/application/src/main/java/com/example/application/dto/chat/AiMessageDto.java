package com.example.application.dto.chat;

import com.example.application.entity.ChatHistory.StageContext;
import com.example.application.entity.ChatHistory.FeatureContext;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

// 서버 → 사용자 전송용 (AI 응답)
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class AiMessageDto {
    private String userId;
    private Long bookId;
    @Builder.Default
    private String sender = "AI";
    private String content;
    private String messageType; // TEXT, .. (추후 확장 예정)

    private FeatureContext featureContext;
    private StageContext stageContext;

    // 추가 필드 예시
    // private String source; // langchain, api, vectorDB 등
    // private List<String> references;
    // private Boolean requiresFollowup;
}