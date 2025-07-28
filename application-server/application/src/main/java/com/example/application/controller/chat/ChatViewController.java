package com.example.application.controller.chat;

import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;

@Controller
public class ChatViewController {
    @GetMapping("/chat")
    public String getChatPage(@RequestParam Long userId,
                              @RequestParam Long bookId,
                              Model model) {
        model.addAttribute("userId", userId);
        model.addAttribute("bookId", bookId);
        return "page/chat"; // templates/page/chat.html 렌더링
    }

}