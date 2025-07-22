package com.example.application.controller.chat;

import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;

import java.util.Arrays;
import java.util.List;
import java.util.Map;

@Controller
public class ChatViewController {

    @GetMapping("/chat")
    public String getChatPage(Model model) {
        List<Map<String, String>> chatMessages = Arrays.asList(
                Map.of("sender", "user", "content", "안녕하세요!", "timestamp", "2024-07-18 10:00"),
                Map.of("sender", "bot", "content", "안녕하세요! 무엇을 도와드릴까요?", "timestamp", "2024-07-18 10:01"),
                Map.of("sender", "user", "content", "챗봇 테스트 중입니다.", "timestamp", "2024-07-18 10:02")
        );
        model.addAttribute("chatMessages", chatMessages);
        return "chat";
    }
}