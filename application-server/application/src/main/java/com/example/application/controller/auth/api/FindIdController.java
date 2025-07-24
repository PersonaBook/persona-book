package com.example.application.controller.auth.api;

import com.example.application.payload.response.MessageResponse;
import com.example.application.service.AuthService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@Controller
public class FindIdController {

    @Autowired
    private AuthService authService;

    @GetMapping("/idInquiry")
    public String findIdView() {
        return "user/idInquiry";
    }

    @PostMapping("/find-id-success")
    public String findIdSuccess(Model model) {
        model.addAttribute("title", "아이디 찾기 완료");
        return "user/findIdSuccess";
    }

    @PostMapping("/api/findId/sendVerificationEmail")
    @ResponseBody
    public ResponseEntity<?> sendVerificationEmailFindId(@RequestBody Map<String, String> request) {
        String email = request.get("email");
        if (email == null || email.isEmpty()) {
            return ResponseEntity.badRequest().body(new MessageResponse(HttpStatus.BAD_REQUEST, "Email is required."));
        }
        if (authService.sendEmailVerificationCode(email, true)) {
            return ResponseEntity.ok(new MessageResponse(HttpStatus.OK, "Verification code sent successfully."));
        } else {
            return ResponseEntity.badRequest().body(new MessageResponse(HttpStatus.BAD_REQUEST, "Failed to send verification code. Please try again."));
        }
    }

    @PostMapping("/api/findId/verifyCode")
    @ResponseBody
    public ResponseEntity<?> verifyCodeFindId(@RequestBody Map<String, String> request) {
        String email = request.get("email");
        String code = request.get("code");
        if (email == null || email.isEmpty() || code == null || code.isEmpty()) {
            return ResponseEntity.badRequest().body(new MessageResponse(HttpStatus.BAD_REQUEST, "Email and code are required."));
        }
        if (authService.verifyEmailCode(email, code)) {
            return ResponseEntity.ok(new MessageResponse(HttpStatus.OK, "Verification successful."));
        } else {
            return ResponseEntity.badRequest().body(new MessageResponse(HttpStatus.BAD_REQUEST, "Invalid or expired verification code."));
        }
    }

    @GetMapping("/findIdSuccess")
    public String findIdSuccess(@RequestParam(value = "userId", required = false) String userId, org.springframework.ui.Model model) {
        model.addAttribute("userId", userId);
        return "page/findIdSuccess";
    }

    @PostMapping("/api/findId")
    @ResponseBody
    public ResponseEntity<?> findId(@RequestBody Map<String, String> request) {
        String email = request.get("email");
        if (email == null || email.isEmpty()) {
            return ResponseEntity.badRequest().body(new MessageResponse(HttpStatus.BAD_REQUEST, "Email is required."));
        }
        String username = authService.findUsernameByEmail(email);
        if (username != null) {
            return ResponseEntity.ok(new MessageResponse(HttpStatus.OK, "Your username is: " + username));
        } else {
            return ResponseEntity.status(HttpStatus.NOT_FOUND).body(new MessageResponse(HttpStatus.NOT_FOUND, "No user found with that email address."));
        }
    }
}