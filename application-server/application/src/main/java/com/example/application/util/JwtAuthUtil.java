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
        String bearer = request.getHeader("Authorization");
        if (bearer != null && bearer.startsWith("Bearer ")) {
            token = bearer.substring(7);
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