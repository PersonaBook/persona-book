package com.example.application.util;

import com.example.application.entity.User;
import com.example.application.repository.UserRepository;
import com.example.application.security.jwt.JwtTokenProvider;
import jakarta.servlet.http.HttpServletRequest;
import org.springframework.stereotype.Component;

@Component
public class JwtAuthUtil {
    
    private final JwtTokenProvider jwtTokenProvider;
    private final UserRepository userRepository;

    public JwtAuthUtil(JwtTokenProvider jwtTokenProvider, UserRepository userRepository) {
        this.jwtTokenProvider = jwtTokenProvider;
        this.userRepository = userRepository;
    }

    public User getUserFromRequest(HttpServletRequest request) {
        String token = null;
        
        // Authorization 헤더에서 토큰 확인 (보안상 URL 파라미터 제거)
        String bearer = request.getHeader("Authorization");
        if (bearer != null && bearer.startsWith("Bearer ")) {
            token = bearer.substring(7);
        }
        
        // Authorization 헤더에 토큰이 없으면 세션에서 확인
        if (token == null) {
            token = (String) request.getSession().getAttribute("loginToken");
        }
        
        if (token == null || !jwtTokenProvider.validateToken(token)) {
            return null;
        }
        String email;
        try {
            email = jwtTokenProvider.getUserNameFromJwtToken(token);
        } catch (Exception e) {
            return null;
        }
        return userRepository.findByUserEmail(email).orElse(null);
    }
} 