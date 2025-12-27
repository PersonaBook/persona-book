package com.example.application.domain.auth.controller;

import com.example.application.domain.auth.dto.request.LoginRequestDto;
import com.example.application.domain.auth.dto.request.RegisterRequestDto;
import com.example.application.domain.auth.dto.request.RefreshTokenRequestDto;
import com.example.application.domain.auth.dto.response.LoginResponseDto;
import com.example.application.domain.auth.dto.response.MessageResponseDto;
import com.example.application.domain.auth.service.AuthService;
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
    @PostMapping("/login")
    public ResponseEntity<?> login(@Valid @RequestBody LoginRequestDto request, HttpSession session) {
        try {
            LoginResponseDto response = authService.login(request, session);
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            return ResponseEntity.badRequest().body(new MessageResponseDto(HttpStatus.BAD_REQUEST, e.getMessage()));
        }
    }

    // 회원가입
    @PostMapping("/register")
    public ResponseEntity<?> register(@Valid @RequestBody RegisterRequestDto request) {
        try {
            authService.register(request);
            return ResponseEntity.ok(new MessageResponseDto(HttpStatus.OK, "회원가입이 완료되었습니다. 이메일 인증을 확인해주세요."));
        } catch (Exception e) {
            return ResponseEntity.badRequest().body(new MessageResponseDto(HttpStatus.BAD_REQUEST, e.getMessage()));
        }
    }
    
    // 로그인 토큰 만료시 계속 유지시키기 위한 리프레쉬 토큰
    @PostMapping("/token/refresh")
    public ResponseEntity<?> refreshToken(@Valid @RequestBody RefreshTokenRequestDto request, HttpSession session) {
        try {
            LoginResponseDto response = authService.refreshToken(request.getRefreshToken(), session);
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body(new MessageResponseDto(HttpStatus.UNAUTHORIZED, e.getMessage()));
        }
    }

    // 로그아웃
    @PostMapping("/logout")
    public ResponseEntity<?> logout(HttpSession session) {
        authService.logout(session);
        return ResponseEntity.ok(new MessageResponseDto(HttpStatus.OK, "Log out successful!"));
    }

    // 이메일 인증
    @PostMapping("/email/verify")
    public ResponseEntity<?> verifyEmail(@RequestBody Map<String, String> request) {
        String email = request.get("email");
        String code = request.get("code");

        if (email == null || email.isEmpty() || code == null || code.isEmpty()) {
            return ResponseEntity.badRequest().body(new MessageResponseDto(HttpStatus.BAD_REQUEST, "이메일과 인증코드가 필요합니다."));
        }

        try {
            authService.verifyEmail(email, code);
            return ResponseEntity.ok(new MessageResponseDto(HttpStatus.OK, "이메일 인증에 성공했습니다."));
        } catch (Exception e) {
            return ResponseEntity.badRequest().body(new MessageResponseDto(HttpStatus.BAD_REQUEST, e.getMessage()));
        }
    }

    // 이메일 인증번호 보내기
    @PostMapping("/email/send")
    public ResponseEntity<?> sendEmail(@RequestBody Map<String, String> request) {
        String email = request.get("email");
        String type = request.get("type");
        
        if (email == null || email.isEmpty()) {
            return ResponseEntity.badRequest().body(new MessageResponseDto(HttpStatus.BAD_REQUEST, "이메일이 필요합니다."));
        }

        boolean mustExist = "findId".equals(type) || "findPassword".equals(type);

        try {
            authService.requestVerificationCode(email, mustExist);
            return ResponseEntity.ok(new MessageResponseDto(HttpStatus.OK, "인증번호를 발송했습니다."));
        } catch (Exception e) {
            return ResponseEntity.badRequest().body(new MessageResponseDto(HttpStatus.BAD_REQUEST, e.getMessage()));
        }
    }

    // ID 찾기
    @PostMapping("/id/find")
    public ResponseEntity<?> findId(@RequestBody Map<String, String> request) {
        String name = request.get("name");
        String email = request.get("email");

        if (name == null || name.isEmpty() || email == null || email.isEmpty()) {
            return ResponseEntity.badRequest().body(new MessageResponseDto(HttpStatus.BAD_REQUEST, "이름과 이메일이 모두 필요합니다."));
        }

        try {
            String username = authService.findId(name, email);
            return ResponseEntity.ok(new MessageResponseDto(HttpStatus.OK, "귀하의 아이디는: " + username));
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.NOT_FOUND).body(new MessageResponseDto(HttpStatus.NOT_FOUND, e.getMessage()));
        }
    }

    @PostMapping("/password/reset")
    public ResponseEntity<?> resetPassword(@RequestBody Map<String, String> request) {
        String name = request.get("name");
        String email = request.get("email");
        String newPassword = request.get("newPassword");

        if (name == null || name.isEmpty() || email == null || email.isEmpty() ||
            newPassword == null || newPassword.isEmpty()) {
            return ResponseEntity.badRequest().body(new MessageResponseDto(HttpStatus.BAD_REQUEST, "이름, 이메일, 비밀번호가 모두 필요합니다."));
        }

        try {
            authService.resetPassword(name, email, newPassword);
            return ResponseEntity.ok(new MessageResponseDto(HttpStatus.OK, "비밀번호가 성공적으로 변경되었습니다."));
        } catch (Exception e) {
            return ResponseEntity.badRequest().body(new MessageResponseDto(HttpStatus.BAD_REQUEST, e.getMessage()));
        }
    }
}
