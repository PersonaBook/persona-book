package com.example.application.domain.chat.dto.response;

import com.example.application.domain.chat.type.ChatState;
import com.example.application.domain.chat.type.MessageType;
import com.example.application.domain.chat.type.Sender;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

@Getter
@Builder
@AllArgsConstructor
@NoArgsConstructor
public class GeneratingQuestionResponseDto {
    private Long userId;
    private Long bookId;
    @Builder.Default
    private Sender sender = Sender.AI;
    private String content;
    @Builder.Default
    private MessageType messageType = MessageType.TEXT; // TEXT, .. (추후 확장 예정)

    private ChatState chatState;

    private String domain; // 문제 도메인
    private String concept; // 문제 개념
    private String questionText; // 실제 문제 문장
    private String correctAnswer; // 정답
}