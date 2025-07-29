package com.example.application.controller.auth.api;

import com.example.application.dto.auth.response.MessageResponse;
import com.example.application.service.AuthService;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@Controller
public class FindIdController {

    private final AuthService authService;
    
    public FindIdController(AuthService authService) {
        this.authService = authService;
    }


    @PostMapping("/api/findId")
    @ResponseBody
    public ResponseEntity<?> findId(@RequestBody Map<String, String> request) {
        String userName = request.get("userName");
        String email = request.get("email");
        
        if (userName == null || userName.isEmpty() || email == null || email.isEmpty()) {
            return ResponseEntity.badRequest().body(new MessageResponse(HttpStatus.BAD_REQUEST, "이름과 이메일이 모두 필요합니다."));
        }
        
        String username = authService.findUsernameByNameAndEmail(userName, email);
        if (username != null) {
            return ResponseEntity.ok(new MessageResponse(HttpStatus.OK, "귀하의 아이디는: " + username));
        } else {
            return ResponseEntity.status(HttpStatus.NOT_FOUND).body(new MessageResponse(HttpStatus.NOT_FOUND, "이름과 이메일이 일치하지 않습니다."));
        }
    }
}