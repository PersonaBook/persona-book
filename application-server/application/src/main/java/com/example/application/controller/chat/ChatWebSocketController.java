package com.example.application.controller.chat;

import com.example.application.dto.chat.UserMessageDto;
import com.example.application.service.ChatService;
import lombok.RequiredArgsConstructor;
import org.springframework.messaging.handler.annotation.Header;
import org.springframework.messaging.handler.annotation.MessageMapping;
import org.springframework.messaging.handler.annotation.Payload;
import org.springframework.messaging.simp.SimpMessagingTemplate;
import org.springframework.stereotype.Controller;

@Controller
@RequiredArgsConstructor
public class ChatWebSocketController {

    private final ChatService chatService;
    private final SimpMessagingTemplate messagingTemplate;

    @MessageMapping("/chat/message")
    public void handleUserMessage(@Payload UserMessageDto userMessageDto,
                                  @Header("bookId") Long bookId) {
        // 서비스로 메시지를 전달하고, 응답을 브로드캐스트
        chatService.handleUserMessage(userMessageDto, bookId)
                .subscribe(aiMessageDto ->
                        messagingTemplate.convertAndSend("/topic/chat", aiMessageDto)
                );
    }
}
