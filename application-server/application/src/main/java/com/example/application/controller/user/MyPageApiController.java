package com.example.application.controller.user;

import com.example.application.entity.User;
import com.example.application.util.JwtAuthUtil;
import jakarta.servlet.http.HttpServletRequest;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

@RestController
@RequestMapping("/api")
class MyPageApiController {
    @Autowired
    private JwtAuthUtil jwtAuthUtil;

    @GetMapping("/myPage")
    public ResponseEntity<?> getMyPage(HttpServletRequest request) {
        User user = jwtAuthUtil.getUserFromRequest(request);
        if (user == null) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body("인증 필요");
        }
        Map<String, Object> result = new java.util.HashMap<>();
        result.put("userName", user.getUserName());
        result.put("userEmail", user.getUserEmail());
        result.put("userPhoneNumber", user.getUserPhoneNumber());
        result.put("userBirthDate", user.getUserBirthDate());
        result.put("userJob", user.getUserJob());
        result.put("userId", user.getUserId());
        return ResponseEntity.ok(result);
    }
}
