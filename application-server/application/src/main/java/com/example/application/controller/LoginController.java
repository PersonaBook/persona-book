package com.example.application.controller;

import com.example.application.payload.request.LoginRequest;
import com.example.application.payload.response.JwtResponse;
import com.example.application.service.AuthService;
import jakarta.servlet.http.HttpSession;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.servlet.mvc.support.RedirectAttributes;

@Controller
public class LoginController {

    @Autowired
    private AuthService authService;

    @GetMapping("/login")
    public String login(Model model){
        model.addAttribute("title", "로그인");
        return "user/login";
    }

    @PostMapping("/user/login")
    public String loginProcess(String email, String password, HttpSession session, Model model) {
        try {
            // HTML 폼 데이터를 LoginRequest 객체로 변환
            LoginRequest loginRequest = new LoginRequest();
            loginRequest.setUserEmail(email);
            loginRequest.setPassword(password);
            
            // AuthService에서 DB 비교 + JWT 토큰 생성
            JwtResponse jwtResponse = authService.authenticateUser(loginRequest, session);
            
            // 세션에 토큰 저장하고 메인으로 리다이렉트
            session.setAttribute("loginToken", jwtResponse.getToken());
            
            return "redirect:/?token=" + jwtResponse.getToken();
        } catch (Exception e) {
            model.addAttribute("loginError", "로그인에 실패했습니다. 이메일 또는 비밀번호를 확인해주세요.");
            return "user/login";
        }
    }
}