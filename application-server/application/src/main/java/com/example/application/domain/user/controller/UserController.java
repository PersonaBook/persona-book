package com.example.application.domain.user.controller;

import com.example.application.domain.auth.dto.response.MessageResponseDto;
import com.example.application.domain.auth.dto.response.UserProfileResponseDto;
import com.example.application.domain.user.entity.User;
import com.example.application.domain.user.repositroy.UserRepository;
import com.example.application.domain.auth.service.AuthService;
import com.example.application.global.util.JwtAuthUtil;
import jakarta.servlet.http.HttpServletRequest;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api/user")
class UserController {

    private final JwtAuthUtil jwtAuthUtil;
    private final AuthService authService;
    private final UserRepository userRepository;

    public UserController(JwtAuthUtil jwtAuthUtil, AuthService authService, UserRepository userRepository) {
        this.jwtAuthUtil = jwtAuthUtil;
        this.authService = authService;
        this.userRepository = userRepository;
    }

    @GetMapping("/profile")
    public ResponseEntity<?> getProfile(HttpServletRequest request) {
        User user = jwtAuthUtil.getUserFromRequest(request);
        if (user == null) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body("인증 필요");
        }
        Map<String, Object> result = new java.util.HashMap<>();
        result.put("name", user.getName());
        result.put("email", user.getEmail());
        result.put("phoneNumber", user.getPhoneNumber());
        result.put("birthDate", user.getBirthDate());
        result.put("job", user.getJob());
        result.put("userId", user.getUserId());
        return ResponseEntity.ok(result);
    }

    @GetMapping("/{userId}")
    public ResponseEntity<?> getUserById(@PathVariable Long userId) {
        UserProfileResponseDto userProfile = authService.getUserProfile(userId);
        if (userProfile != null) {
            return ResponseEntity.ok(userProfile);
        } else {
            return ResponseEntity.status(HttpStatus.NOT_FOUND).body(new MessageResponseDto(HttpStatus.NOT_FOUND, "사용자를 찾을 수 없습니다."));
        }
    }

    @PostMapping("/profile/update")
    public ResponseEntity<?> updateProfile(HttpServletRequest request, @RequestParam(required = false) String name,
                                          @RequestParam(required = false) String email,
                                          @RequestParam(required = false) String phoneNumber,
                                          @RequestParam(required = false) String birthDate,
                                          @RequestParam(required = false) String job,
                                          @RequestParam(required = false) String otherUserJob) {
        User user = jwtAuthUtil.getUserFromRequest(request);
        if (user == null) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body(new MessageResponseDto(HttpStatus.UNAUTHORIZED, "인증이 필요합니다. 다시 로그인 해주세요."));
        }
        if (name != null && !name.isBlank()) user.setName(name);
        if (email != null && !email.isBlank()) user.setEmail(email);
        if (phoneNumber != null && !phoneNumber.isBlank()) user.setPhoneNumber(phoneNumber);
        if (birthDate != null && !birthDate.isBlank()) user.setBirthDate(java.time.LocalDate.parse(birthDate));
        if (job != null && !job.isBlank()) {
            if (job.equals("other") && otherUserJob != null && !otherUserJob.isBlank()) {
                user.setJob(otherUserJob);
            } else {
                user.setJob(job);
            }
        }
        userRepository.save(user);
        return ResponseEntity.ok(new MessageResponseDto(HttpStatus.OK, "회원정보가 성공적으로 수정되었습니다."));
    }
}
