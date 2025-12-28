package com.example.application.domain.chat.controller;

import com.example.application.domain.chat.dto.AiMessageDto;
import com.example.application.domain.chat.dto.UserMessageDto;
import com.example.application.domain.chat.dto.response.ChatHistoryResponseDto;
import com.example.application.domain.chat.service.ChatHistoryService;
import com.example.application.domain.chat.service.ChatService;
import com.example.application.global.dto.ApiResponseDto;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequiredArgsConstructor
@RequestMapping("/api/chat")
public class ChatController {

    private final ChatService chatService;
    private final ChatHistoryService chatHistoryService;

    @PostMapping("/send")
    public ApiResponseDto<List<AiMessageDto>> sendMessage(
            @RequestAttribute("userId") Long userId,
            @Valid @RequestBody UserMessageDto userMessageDto
    ) {
        return ApiResponseDto.success(chatService.handleChatFlow(userId, userMessageDto));
    }

    @GetMapping("/history")
    public ApiResponseDto<List<ChatHistoryResponseDto>> getChatHistory(
            @RequestAttribute("userId") Long userId,
            @RequestParam Long bookId
    ) {
        return ApiResponseDto.success(chatHistoryService.getChatHistory(userId, bookId));
    }

    @DeleteMapping("/history")
    public ApiResponseDto<Void> deleteChatHistory(
            @RequestAttribute("userId") Long userId,
            @RequestParam Long bookId
    ) {
        chatHistoryService.deleteChatHistory(userId, bookId);
        return ApiResponseDto.success("채팅 기록이 삭제되었습니다.");
    }

    @GetMapping("/ping")
    public ApiResponseDto<String> pingFastApi() {
        chatService.checkFastApiConnection();
        return ApiResponseDto.success("Pong (AI Server Connected)");
    }
}