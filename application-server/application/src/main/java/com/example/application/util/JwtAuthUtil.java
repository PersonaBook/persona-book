package com.example.application.util;

import com.example.application.entity.User;
import com.example.application.repository.UserRepository;
import com.example.application.security.jwt.JwtTokenProvider;
import jakarta.servlet.http.HttpServletRequest;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;

@Component
public class JwtAuthUtil {
    @Autowired
    private JwtTokenProvider jwtTokenProvider;
    @Autowired
    private UserRepository userRepository;

    public User getUserFromRequest(HttpServletRequest request) {
        String token = null;
        
        // 먼저 URL 파라미터에서 토큰 확인
        token = request.getParameter("token");
        
        // URL 파라미터에 토큰이 없으면 Authorization 헤더에서 확인
        if (token == null) {
            String bearer = request.getHeader("Authorization");
            if (bearer != null && bearer.startsWith("Bearer ")) {
                token = bearer.substring(7);
            }
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