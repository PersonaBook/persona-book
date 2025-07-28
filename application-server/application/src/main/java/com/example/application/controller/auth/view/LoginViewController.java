package com.example.application.controller.auth.view;

import com.example.application.dto.auth.request.LoginRequest;
import com.example.application.dto.auth.response.JwtResponse;
import com.example.application.service.AuthService;
import jakarta.servlet.http.HttpSession;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;

@Controller
public class LoginViewController {

    private final AuthService authService;
    
    public LoginViewController(AuthService authService) {
        this.authService = authService;
    }

    @GetMapping("/login")
    public String login(Model model){
        model.addAttribute("title", "로그인");
        return "user/login";
    }

    @PostMapping("/user/login")
    public String loginProcess(String email, String password, Boolean rememberMe, HttpSession session, Model model) {
        try {
            // HTML 폼 데이터를 LoginRequest 객체로 변환
            LoginRequest loginRequest = new LoginRequest();
            loginRequest.setUserEmail(email);
            loginRequest.setPassword(password);
            loginRequest.setRememberMe(rememberMe != null && rememberMe);
            
            // AuthService에서 DB 비교 + JWT 토큰 생성
            JwtResponse jwtResponse = authService.authenticateUser(loginRequest, session);
            
            // rememberMe 정보도 URL에 포함해서 프론트엔드에서 처리
            String rememberMeParam = loginRequest.isRememberMe() ? "&rememberMe=true" : "&rememberMe=false";
            return "redirect:/?token=" + jwtResponse.getToken() + "&refresh=true" + rememberMeParam;
        } catch (Exception e) {
            model.addAttribute("loginError", "로그인에 실패했습니다. 이메일 또는 비밀번호를 확인해주세요.");
            return "user/login";
        }
    }
}