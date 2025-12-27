package com.example.application.domain.auth.controller;

import com.example.application.domain.auth.dto.request.LoginRequestDto;
import com.example.application.domain.auth.dto.request.RegisterRequestDto;
import com.example.application.domain.auth.dto.response.LoginResponseDto;
import com.example.application.domain.auth.service.AuthService;
import jakarta.servlet.http.HttpSession;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.servlet.mvc.support.RedirectAttributes;

@Controller
@RequiredArgsConstructor
@Slf4j
@RequestMapping("/auth")
public class AuthViewController {

    private final AuthService authService;

    @GetMapping("/login")
    public String getLoginPage(Model model){
        model.addAttribute("title", "로그인");
        return "page/auth/login";
    }

    @PostMapping("/login")
    public String processLogin(@ModelAttribute LoginRequestDto request, HttpSession session, Model model) {
        try {
            LoginResponseDto response = authService.login(request, session);

            String autoLoginParam = request.isAutoLogin() ? "&autoLogin=true" : "&autoLogin=false";
            return "redirect:/?token=" + response.getToken() + "&refresh=true" + autoLoginParam;

        } catch (Exception e) {
            log.warn("로그인 실패: {}", e.getMessage());
            // 에러 발생 시 다시 로그인 페이지로 이동하며 에러 메시지 전달
            model.addAttribute("loginError", e.getMessage()); // Service에서 던진 구체적인 메시지 사용
            model.addAttribute("title", "로그인");
            return "page/auth/login";
        }
    }

    @GetMapping("/register")
    public String getRegisterPage(Model model) {
        model.addAttribute("title", "회원가입");
        return "page/auth/register";
    }

    @PostMapping("/register")
    public String processRegistration(@ModelAttribute RegisterRequestDto request, Model model, RedirectAttributes redirectAttributes) {
        try {
            // boolean 반환이 아니라 void이므로, 성공하면 다음 줄로 진행
            authService.register(request);

            // 성공 시 로그인 페이지나 메인으로 리다이렉트
            redirectAttributes.addFlashAttribute("message", "회원가입이 완료되었습니다! 이메일 인증을 진행해주세요.");
            return "redirect:/auth/login"; // 보통 가입 후엔 로그인 페이지로 보냄

        } catch (Exception e) {
            log.warn("회원가입 실패: {}", e.getMessage());
            // 실패 시 다시 가입 페이지로 + 에러 메시지
            model.addAttribute("errorMessage", e.getMessage()); // "이미 존재하는 이메일입니다" 등
            model.addAttribute("title", "회원가입");
            return "page/auth/register";
        }
    }

    @GetMapping("/id/find")
    public String getFindIdPage() {
        return "page/auth/find-id";
    }

    @GetMapping("/id/find/success")
    public String getFindIdSuccessPage(@RequestParam(value = "userId", required = false) String userId, Model model) {
        model.addAttribute("userId", userId);
        return "page/auth/find-id-success";
    }

    @GetMapping("/password/find")
    public String getFindPasswordPage() {
        return "page/auth/find-password";
    }

    @GetMapping("/password/find/success")
    public String getFindPasswordSuccessPage() {
        return "page/auth/find-password-success";
    }
}
