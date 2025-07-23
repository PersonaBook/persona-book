package com.example.application.controller;

import com.example.application.payload.response.MessageResponse;
import com.example.application.service.AuthService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@Controller
public class FindPasswordController {

    @Autowired
    private AuthService authService;

    @GetMapping("/pwInquiry")
    public String findPasswordView() {
        return "user/pwInquiry";
    }

    @PostMapping("/api/findPassword/sendVerificationEmail")
    @ResponseBody
    public ResponseEntity<?> sendVerificationEmailFindPassword(@RequestBody Map<String, String> request) {
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

    @PostMapping("/api/findPassword/verifyCode")
    @ResponseBody
    public ResponseEntity<?> verifyCodeFindPassword(@RequestBody Map<String, String> request) {
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

    @GetMapping("/findPasswordSuccess")
    public String findPasswordSuccess() {
        return "page/findPasswordSuccess";
    }

    @PostMapping("/api/findPassword/reset")
    @ResponseBody
    public ResponseEntity<?> resetPassword(@RequestBody Map<String, String> request) {
        String email = request.get("email");
        String verificationCode = request.get("verificationCode");
        String newPassword = request.get("newPassword");

        if (email == null || email.isEmpty() || verificationCode == null || verificationCode.isEmpty() || newPassword == null || newPassword.isEmpty()) {
            return ResponseEntity.badRequest().body(new MessageResponse(HttpStatus.BAD_REQUEST, "All fields are required."));
        }

        try {
            authService.resetPassword(email, verificationCode, newPassword);
            return ResponseEntity.ok(new MessageResponse(HttpStatus.OK, "Password has been reset successfully."));
        } catch (Exception e) {
            return ResponseEntity.badRequest().body(new MessageResponse(HttpStatus.BAD_REQUEST, e.getMessage()));
        }
    }

    @PostMapping("/api/resetPassword")
    @ResponseBody
    public ResponseEntity<?> forgotPassword(@RequestBody Map<String, String> request) {
        String email = request.get("email");
        if (email == null || email.isEmpty()) {
            return ResponseEntity.badRequest().body(new MessageResponse(HttpStatus.BAD_REQUEST, "Email is required."));
        }
        if (authService.forgotPassword(email)) {
            return ResponseEntity.ok(new MessageResponse(HttpStatus.OK, "Password reset email sent. Please check your inbox."));
        } else {
            return ResponseEntity.status(HttpStatus.NOT_FOUND).body(new MessageResponse(HttpStatus.NOT_FOUND, "No user found with that email address."));
        }
    }
}