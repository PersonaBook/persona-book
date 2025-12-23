package com.example.application.controller.auth;

import com.example.application.dto.auth.request.LoginRequestDto;
import com.example.application.dto.auth.request.RegisterRequestDto;
import com.example.application.dto.auth.response.LoginResponseDto;
import com.example.application.service.AuthService;
import jakarta.servlet.http.HttpSession;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.servlet.mvc.support.RedirectAttributes;

@Controller
@RequestMapping("/auth")
public class AuthViewController {

    private final AuthService authService;

    @Autowired
    public AuthViewController(AuthService authService) {
        this.authService = authService;
    }

    @GetMapping("/login")
    public String getLoginPage(Model model){
        model.addAttribute("title", "로그인");
        return "page/auth/login";
    }

    @PostMapping("/login")
    public String processLogin(String email, String password, Boolean autoLogin, HttpSession session, Model model) {
        try {
            LoginRequestDto loginRequestDto = new LoginRequestDto();
            loginRequestDto.setEmail(email);
            loginRequestDto.setPassword(password);
            loginRequestDto.setAutoLogin(autoLogin != null && autoLogin);
            
            LoginResponseDto loginResponse = authService.authenticateUser(loginRequestDto, session);
            
            String autoLoginParam = loginRequestDto.isAutoLogin() ? "&autoLogin=true" : "&autoLogin=false";
            return "redirect:/?token=" + loginResponse.getToken() + "&refresh=true" + autoLoginParam;
        } catch (Exception e) {
            model.addAttribute("loginError", "로그인에 실패했습니다. 이메일 또는 비밀번호를 확인해주세요.");
            return "page/auth/login";
        }
    }

    @GetMapping("/register")
    public String getRegisterPage(Model model) {
        model.addAttribute("title", "회원가입");
        return "page/auth/register";
    }

    @PostMapping("/register")
    public String processRegistration(RegisterRequestDto registerRequest, Model model, RedirectAttributes redirectAttributes) {
        if (authService.registerUser(registerRequest)) {
            redirectAttributes.addFlashAttribute("message", "회원가입이 완료되었습니다! 이메일 인증을 진행해주세요.");
            return "redirect:/";
        } else {
            model.addAttribute("errorMessage", "회원가입에 실패했습니다. 사용자 이름 또는 이메일이 이미 존재합니다.");
            return "page/auth/register";
        }
    }

    @GetMapping("/find-id")
    public String getFindIdPage() {
        return "page/auth/find-id";
    }

    @GetMapping("/find-id/success")
    public String getFindIdSuccessPage(@RequestParam(value = "userId", required = false) String userId, Model model) {
        model.addAttribute("userId", userId);
        return "page/auth/find-id-success";
    }

    @GetMapping("/find-password")
    public String getFindPasswordPage() {
        return "page/auth/find-password";
    }

    @GetMapping("/find-password/success")
    public String getFindPasswordSuccessPage() {
        return "page/auth/find-password-success";
    }
}
