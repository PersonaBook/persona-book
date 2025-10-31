package com.example.application.dto.chat;

import com.example.application.entity.ChatHistory.ChatState;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.Setter;

@Getter
@Setter // DTO의 불변성을 유지하기 위해서 @Setter를 사용하지 않아야 하지만, 해당 DTO의 경우 상태 전이 로직 상 필요
@Builder
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
}