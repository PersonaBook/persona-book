package com.example.application.domain.chat.controller;

import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;

@Controller
public class ChatViewController {
    // 테스트를 위한 페이지
    // `/chat?userId={사용자_ID}&bookId={책_ID}`
    @GetMapping("/chat")
    public String getChatPage(@RequestParam Long userId,
                              @RequestParam Long bookId,
                              Model model) {
        model.addAttribute("userId", userId);
        model.addAttribute("bookId", bookId);
        return "page/chat";
    }

}