package com.example.application.domain.chat.controller;

import com.example.application.domain.chat.dto.AiMessageDto;
import com.example.application.domain.chat.dto.UserMessageDto;
import com.example.application.domain.chat.entity.ChatHistory;
import com.example.application.domain.chat.service.ChatHistoryService;
import com.example.application.domain.chat.service.ChatService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequiredArgsConstructor
@RequestMapping("/api/chat")
public class ChatController {

    private final ChatService chatService;
    private final ChatHistoryService chatHistoryService;

    @PostMapping("/send")
    public List<AiMessageDto> sendMessage(@RequestBody UserMessageDto userMessageDto) {
        return chatService.handleChatFlow(userMessageDto);
    }

    @GetMapping("/history")
    public ResponseEntity<List<ChatHistory>> getChatHistory(
            @RequestParam Long userId,
            @RequestParam Long bookId
    ) {
        return ResponseEntity.ok(chatHistoryService.getChatHistory(userId, bookId));
    }

    @DeleteMapping("/history")
    public ResponseEntity<Void> deleteChatHistory(
            @RequestParam Long userId,
            @RequestParam Long bookId
    ) {
        chatHistoryService.deleteChatHistory(userId, bookId);
        return ResponseEntity.noContent().build();
    }

    @GetMapping("/ping")
    public ResponseEntity<String> pingFastApi() {
        boolean connected = chatService.checkFastApiConnection();
        return connected ? ResponseEntity.ok("pong") : ResponseEntity.status(503).body("LangChain unavailable");
    }
}