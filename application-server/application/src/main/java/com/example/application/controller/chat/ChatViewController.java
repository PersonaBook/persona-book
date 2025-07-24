package com.example.application.controller.chat;

import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;

@Controller
public class ChatViewController {

    @GetMapping("/chat")
    public String getChatPage(Model model) {
        model.addAttribute("userId", 1001);
        model.addAttribute("bookId", 1);

        return "chat"; // templates/chat.html 을 렌더링
    }
}