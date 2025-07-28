package com.example.application.controller.auth.api;

import com.example.application.payload.request.LoginRequest;
import com.example.application.payload.request.SignupRequest;
import com.example.application.payload.request.TokenRefreshRequest;
import com.example.application.payload.response.JwtResponse;
import com.example.application.payload.response.MessageResponse;
import com.example.application.payload.response.UserProfileResponse;
import com.example.application.service.AuthService;
import jakarta.servlet.http.HttpSession;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@CrossOrigin(origins = "*", maxAge = 3600)
@RestController
@RequestMapping("/api/auth")
public class AuthController {

    private final AuthService authService;
    
    public AuthController(AuthService authService) {
        this.authService = authService;
    }

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
            return ResponseEntity.badRequest().body(new MessageResponse(HttpStatus.BAD_REQUEST, "이메일과 인증코드가 필요합니다."));
        }
        if (authService.verifyEmailCode(email, code)) {
            return ResponseEntity.ok(new MessageResponse(HttpStatus.OK, "이메일 인증에 성공했습니다."));
        } else {
            return ResponseEntity.badRequest().body(new MessageResponse(HttpStatus.BAD_REQUEST, "만료된 인증 코드입니다."));
        }
    }

    @PostMapping("/sendVerificationEmail")
    public ResponseEntity<?> sendVerificationEmail(@RequestBody Map<String, String> request) {
        String email = request.get("email");
        String type = request.get("type"); // "signup", "findId", "findPassword"
        
        if (email == null || email.isEmpty()) {
            return ResponseEntity.badRequest().body(new MessageResponse(HttpStatus.BAD_REQUEST, "이메일이 필요합니다."));
        }

        // type에 따라 mustExist 파라미터 결정 (type이 없으면 기본값 signup 처리)
        boolean mustExist = "findId".equals(type) || "findPassword".equals(type);

        String result = authService.sendEmailVerificationCode(email, mustExist);
        if ("인증번호를 발송했습니다.".equals(result)) {
            return ResponseEntity.ok(new MessageResponse(HttpStatus.OK, result));
        } else {
            return ResponseEntity.badRequest().body(new MessageResponse(HttpStatus.BAD_REQUEST, result));
        }
    }

    @PostMapping("/findId")
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

    @PostMapping("/resetPassword")
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

    @GetMapping("/profile/{userId}")
    public ResponseEntity<?> getUserProfile(@PathVariable Long userId) {
        UserProfileResponse userProfile = authService.getUserProfile(userId);
        if (userProfile != null) {
            return ResponseEntity.ok(userProfile);
        } else {
            return ResponseEntity.status(HttpStatus.NOT_FOUND).body(new MessageResponse(HttpStatus.NOT_FOUND, "사용자를 찾을 수 없습니다."));
        }
    }
}
