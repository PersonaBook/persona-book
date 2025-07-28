package com.example.application.controller.chat;

import com.example.application.dto.chat.AiMessageDto;
import com.example.application.dto.chat.UserMessageDto;
import com.example.application.entity.ChatHistory;
import com.example.application.service.ChatHistoryService;
import com.example.application.service.ChatService;
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
    public ResponseEntity<String> pingLangChain() {
        boolean connected = chatService.checkLangChainConnection();
        return connected ? ResponseEntity.ok("pong") : ResponseEntity.status(503).body("LangChain unavailable");
    }
}