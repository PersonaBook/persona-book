package com.example.application.controller.auth.api;

import com.example.application.payload.response.MessageResponse;
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

    @PostMapping("/resetPassword")
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