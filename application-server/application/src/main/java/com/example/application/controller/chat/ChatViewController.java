package com.example.application.controller.chat;

import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;

@Controller
public class ChatViewController {

    @GetMapping("/chat")
    public String getChatPage() {
        return "chat"; // templates/chat.html 을 렌더링
    }
}