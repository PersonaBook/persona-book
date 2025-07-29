package com.example.application.controller.auth.api;

import com.example.application.dto.auth.request.LoginRequest;
import com.example.application.dto.auth.request.SignupRequest;
import com.example.application.dto.auth.request.TokenRefreshRequest;
import com.example.application.dto.auth.response.JwtResponse;
import com.example.application.dto.auth.response.MessageResponse;
import com.example.application.dto.auth.response.UserProfileResponse;
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

    // 로그인
    @PostMapping("/signin")
    public ResponseEntity<?> authenticateUser(@Valid @RequestBody LoginRequest loginRequest, HttpSession session) {
        JwtResponse jwtResponse = authService.authenticateUser(loginRequest, session);
        return ResponseEntity.ok(jwtResponse);
    }

    // 회원가입
    @PostMapping("/signup")
    public ResponseEntity<?> registerUser(@Valid @RequestBody SignupRequest signUpRequest) {
        if (authService.registerUser(signUpRequest)) {
            return ResponseEntity.ok(new MessageResponse(HttpStatus.OK, "User registered successfully! Please check your email to verify your account."));
        } else {
            return ResponseEntity.badRequest().body(new MessageResponse(HttpStatus.BAD_REQUEST, "Error: Username or Email is already in use!"));
        }
    }
    
    // 로그인 토큰 만료시 계속 유지시키기 위한 리프레쉬 토큰
    @PostMapping("/refreshtoken")
    public ResponseEntity<?> refreshtoken(@Valid @RequestBody TokenRefreshRequest request, HttpSession session) {
        String refreshToken = request.getRefreshToken();
        JwtResponse jwtResponse = authService.refreshToken(refreshToken, session);
        return ResponseEntity.ok(jwtResponse);
    }

    // 로그아웃
    @PostMapping("/logout")
    public ResponseEntity<?> logoutUser(HttpSession session) {
        authService.logout(session);
        return ResponseEntity.ok(new MessageResponse(HttpStatus.OK, "Log out successful!"));
    }

    // 이메일 인증
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

    // 이메일 인증번호 보내기
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

    // ID 찾기
    @PostMapping("/findId")
    public ResponseEntity<?> findId(@RequestBody Map<String, String> request) {
        String userName = request.get("userName");
        String email = request.get("email");
        
        if (userName == null || userName.isEmpty() || email == null || email.isEmpty()) {
            return ResponseEntity.badRequest().body(new MessageResponse(HttpStatus.BAD_REQUEST, "이름과 이메일이 모두 필요합니다."));
        }
        
        String username = authService.findUsernameByNameAndEmail(userName, email);
        if (username != null) {
            return ResponseEntity.ok(new MessageResponse(HttpStatus.OK, "귀하의 아이디는: " + email));
        } else {
            return ResponseEntity.status(HttpStatus.NOT_FOUND).body(new MessageResponse(HttpStatus.NOT_FOUND, "이름과 이메일이 일치하지 않습니다."));
        }
    }

    // 유저 마이페이지
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
