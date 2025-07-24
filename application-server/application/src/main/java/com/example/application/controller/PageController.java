package com.example.application.controller;

import com.example.application.service.AuthService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.ResponseBody;

import java.util.Map;

@Controller
public class PageController {

    @Autowired
    private AuthService authService;

    @GetMapping("/pdf/main")
    public String pdfMain(Model model) {
        model.addAttribute("title", "PDF로 대화하기");
        return "page/pdfMain";
    }

    @GetMapping("/note/main")
    public String noteMain(Model model) {
        model.addAttribute("title", "내 노트");
        return "page/noteMain";
    }

    @GetMapping("/mypage")
    public String myPage(Model model) {
        model.addAttribute("title", "마이페이지");
        return "page/myPage";
    }

    @GetMapping("/find_id")
    public String findId(Model model) {
        model.addAttribute("title", "아이디 찾기");
        return "idInquiry";
    }



    @GetMapping("/find_password")
    public String findPassword(Model model) {
        model.addAttribute("title", "비밀번호 찾기");
        return "pwInquiry";
    }

    @GetMapping("/find_password_success")
    public String findPasswordSuccess(Model model) {
        model.addAttribute("title", "비밀번호 찾기 완료");
        return "page/findPasswordSuccess";
    }


    @PostMapping("/api/find-id/send-verification-email")
    @ResponseBody
    public ResponseEntity<?> sendFindIdVerificationEmail(@RequestBody Map<String, String> request) {
        String email = request.get("email");
        if (email == null || email.isEmpty()) {
            return ResponseEntity.badRequest().body("Email is required.");
        }
        boolean success = authService.sendEmailVerificationCode(email, true);
        if (success) {
            return ResponseEntity.ok("Verification code sent successfully.");
        } else {
            return ResponseEntity.badRequest().body("Failed to send verification code. Please try again.");
        }
    }

    @PostMapping("/api/find-id/verify-code")
    @ResponseBody
    public ResponseEntity<?> verifyFindIdCode(@RequestBody Map<String, String> request) {
        String email = request.get("email");
        String code = request.get("code");
        if (email == null || email.isEmpty() || code == null || code.isEmpty()) {
            return ResponseEntity.badRequest().body("Email and code are required.");
        }
        boolean success = authService.verifyEmailCode(email, code);
        if (success) {
            return ResponseEntity.ok("Verification successful.");
        } else {
            return ResponseEntity.badRequest().body("Invalid or expired verification code.");
        }
    }

    @PostMapping("/api/find-password/send-verification-email")
    @ResponseBody
    public ResponseEntity<?> sendFindPasswordVerificationEmail(@RequestBody Map<String, String> request) {
        String email = request.get("email");
        if (email == null || email.isEmpty()) {
            return ResponseEntity.badRequest().body("Email is required.");
        }
        boolean success = authService.sendEmailVerificationCode(email, true);
        if (success) {
            return ResponseEntity.ok("Verification code sent successfully.");
        } else {
            return ResponseEntity.badRequest().body("Failed to send verification code. Please try again.");
        }
    }

    @PostMapping("/api/find-password/verify-code")
    @ResponseBody
    public ResponseEntity<?> verifyFindPasswordCode(@RequestBody Map<String, String> request) {
        String email = request.get("email");
        String code = request.get("code");
        if (email == null || email.isEmpty() || code == null || code.isEmpty()) {
            return ResponseEntity.badRequest().body("Email and code are required.");
        }
        boolean success = authService.verifyEmailCode(email, code);
        if (success) {
            return ResponseEntity.ok("Verification successful.");
        } else {
            return ResponseEntity.badRequest().body("Invalid or expired verification code.");
        }
    }
}
