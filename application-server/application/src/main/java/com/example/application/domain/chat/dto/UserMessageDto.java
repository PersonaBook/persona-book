package com.example.application.domain.chat.dto;

import com.example.application.domain.chat.type.ChatState;

import com.example.application.domain.chat.type.MessageType;
import com.example.application.domain.chat.type.Sender;
import lombok.*;

@Getter
@Setter // DTO의 불변성을 유지하기 위해서 @Setter를 사용하지 않아야 하지만, 해당 DTO의 경우 상태 전이 로직 상 필요
@Builder
@AllArgsConstructor
@NoArgsConstructor
public class UserMessageDto {
    private Long userId;
    private Long bookId;
    @Builder.Default
    private Sender sender = Sender.USER;
    private String content;
    @Builder.Default
    private MessageType messageType = MessageType.TEXT; // TEXT, .. (추후 확장 예정)

    private ChatState chatState;
}