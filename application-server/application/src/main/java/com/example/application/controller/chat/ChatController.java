package com.example.application.controller.chat;

import com.example.application.entity.ChatHistory;
import com.example.application.service.ChatHistoryService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
@RequiredArgsConstructor
@RequestMapping("/api/chat")
public class ChatController {

    private final ChatHistoryService chatHistoryService;

    @GetMapping("/history")
    public ResponseEntity<List<ChatHistory>> getChatHistory(
            @RequestParam Long userId,
            @RequestParam Long bookId
    ) {
        return ResponseEntity.ok(chatHistoryService.getChatHistory(userId, bookId));
    }
}
