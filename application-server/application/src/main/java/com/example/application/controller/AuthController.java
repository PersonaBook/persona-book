package com.example.application.controller;

import com.example.application.payload.request.LoginRequest;
import com.example.application.payload.request.SignupRequest;
import com.example.application.payload.request.TokenRefreshRequest;
import com.example.application.payload.response.JwtResponse;
import com.example.application.payload.response.MessageResponse;
import com.example.application.payload.response.UserProfileResponse;
import com.example.application.service.AuthService;
import jakarta.servlet.http.HttpSession;
import jakarta.validation.Valid;
import org.springframework.beans.factory.annotation.Autowired;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@CrossOrigin(origins = "*", maxAge = 3600)
@RestController
@RequestMapping("/api/auth")
public class AuthController {

    @Autowired
    AuthService authService;

    @PostMapping("/signin")
    public ResponseEntity<?> authenticateUser(@Valid @RequestBody LoginRequest loginRequest, HttpSession session) {
        JwtResponse jwtResponse = authService.authenticateUser(loginRequest, session);
        return ResponseEntity.ok(jwtResponse);
    }

    @PostMapping("/signup")
    public ResponseEntity<?> registerUser(@Valid @RequestBody SignupRequest signUpRequest) {
        if (authService.registerUser(signUpRequest)) {
            return ResponseEntity.ok(new MessageResponse(HttpStatus.OK, "User registered successfully! Please check your email to verify your account."));
        } else {
            return ResponseEntity.badRequest().body(new MessageResponse(HttpStatus.BAD_REQUEST, "Error: Username or Email is already in use!"));
        }
    }

    @PostMapping("/refreshtoken")
    public ResponseEntity<?> refreshtoken(@Valid @RequestBody TokenRefreshRequest request, HttpSession session) {
        String refreshToken = request.getRefreshToken();
        JwtResponse jwtResponse = authService.refreshToken(refreshToken, session);
        return ResponseEntity.ok(jwtResponse);
    }

    @PostMapping("/logout")
    public ResponseEntity<?> logoutUser(HttpSession session) {
        authService.logout(session);
        return ResponseEntity.ok(new MessageResponse(HttpStatus.OK, "Log out successful!"));
    }

    @PostMapping("/verifyEmail")
    public ResponseEntity<?> verifyEmail(@RequestBody Map<String, String> request) {
        String email = request.get("email");
        String code = request.get("code");
        if (email == null || email.isEmpty() || code == null || code.isEmpty()) {
            return ResponseEntity.badRequest().body(new MessageResponse(HttpStatus.BAD_REQUEST, "Email and code are required."));
        }
        if (authService.verifyEmailCode(email, code)) {
            return ResponseEntity.ok(new MessageResponse(HttpStatus.OK, "Email verified successfully!"));
        } else {
            return ResponseEntity.badRequest().body(new MessageResponse(HttpStatus.BAD_REQUEST, "Invalid or expired verification code."));
        }
    }

    @PostMapping("/sendVerificationEmail")
    public ResponseEntity<?> sendVerificationEmail(@RequestBody Map<String, String> request) {
        String email = request.get("email");
        if (email == null || email.isEmpty()) {
            return ResponseEntity.badRequest().body(new MessageResponse(HttpStatus.BAD_REQUEST, "Email is required."));
        }

        if (authService.sendEmailVerificationCode(email, false)) {
            return ResponseEntity.ok(new MessageResponse(HttpStatus.OK, "Verification code sent successfully."));
        } else {
            return ResponseEntity.badRequest().body(new MessageResponse(HttpStatus.BAD_REQUEST, "Failed to send verification code. Please try again."));
        }
    }

    @GetMapping("/profile/{userId}")
    
    public ResponseEntity<?> getUserProfile(@PathVariable Long userId) {
        UserProfileResponse userProfile = authService.getUserProfile(userId);
        if (userProfile != null) {
            return ResponseEntity.ok(userProfile);
        } else {
            return ResponseEntity.status(HttpStatus.NOT_FOUND).body(new MessageResponse(HttpStatus.NOT_FOUND, "User not found."));
        }
    }

    
}
