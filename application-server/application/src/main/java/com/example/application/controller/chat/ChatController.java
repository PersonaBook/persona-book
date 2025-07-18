package com.example.application.controller.chat;

import com.example.application.dto.chat.ChatMessage;
import org.springframework.messaging.handler.annotation.*;
import org.springframework.stereotype.Controller;

import java.util.Map;

@Controller
public class ChatController {

    @MessageMapping("/chat/message")
    @SendTo("/topic/chat")
    public ChatMessage send(ChatMessage message,
                            @Header("simpSessionAttributes") Map<String, Object> attributes) {

        // JWT 생략 중이므로 senderId 직접 전달
        if (message.getSenderId() == null) {
            message.setSenderId("anonymous");
        }

        return message; // 구독자들에게 브로드캐스트
    }
}
