package com.example.application.controller.auth.api;

import com.example.application.dto.auth.response.MessageResponse;
import com.example.application.service.AuthService;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@CrossOrigin(origins = "*", maxAge = 3600)
@RestController
@RequestMapping("/api/findPassword")
public class FindPasswordController {

    private final AuthService authService;
    
    public FindPasswordController(AuthService authService) {
        this.authService = authService;
    }






    @PostMapping("/reset")
    public ResponseEntity<?> resetPassword(@RequestBody Map<String, String> request) {
        String userName = request.get("userName");
        String email = request.get("email");
        String newPassword = request.get("newPassword");
        
        System.out.println("=== 비밀번호 재설정 요청 ===");
        System.out.println("UserName: " + userName);
        System.out.println("Email: " + email);
        System.out.println("NewPassword: " + (newPassword != null ? "[입력됨]" : "null"));

        if (userName == null || userName.isEmpty() || email == null || email.isEmpty() || 
            newPassword == null || newPassword.isEmpty()) {
            System.out.println("필수 필드 누락 (이름, 이메일, 비밀번호 모두 필수)");
            return ResponseEntity.badRequest().body(new MessageResponse(HttpStatus.BAD_REQUEST, "이름, 이메일, 비밀번호가 모두 필요합니다."));
        }

        try {
            authService.resetPassword(userName, email, newPassword);
            System.out.println("비밀번호 재설정 성공");
            return ResponseEntity.ok(new MessageResponse(HttpStatus.OK, "비밀번호가 성공적으로 변경되었습니다."));
        } catch (Exception e) {
            System.out.println("비밀번호 재설정 실패: " + e.getMessage());
            e.printStackTrace();
            return ResponseEntity.badRequest().body(new MessageResponse(HttpStatus.BAD_REQUEST, e.getMessage()));
        }
    }

}