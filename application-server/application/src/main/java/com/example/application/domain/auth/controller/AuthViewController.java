package com.example.application.domain.auth.controller;

import com.example.application.domain.auth.dto.request.LoginRequestDto;
import com.example.application.domain.auth.dto.request.RegisterRequestDto;
import com.example.application.domain.auth.dto.response.LoginResponseDto;
import com.example.application.domain.auth.service.AuthService;
import com.example.application.global.exception.CustomException;
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
    public String getLoginPage() {
        return "page/auth/login";
    }

    @PostMapping("/login")
    public String processLogin(@ModelAttribute LoginRequestDto request, Model model) {
        try {
            LoginResponseDto response = authService.login(request);

            return "redirect:/?accessToken=" + response.getAccessToken()
                    + "&refreshToken=" + response.getRefreshToken();

        } catch (CustomException e) {
            log.warn("로그인 실패: {}", e.getErrorCode().getMessage());
            model.addAttribute("loginError", e.getErrorCode().getMessage());
            return "page/auth/login";

        } catch (Exception e) {
            log.error("로그인 시스템 오류", e);
            model.addAttribute("loginError", "로그인 처리 중 오류가 발생했습니다.");
            return "page/auth/login";
        }
    }

    @GetMapping("/register")
    public String getRegisterPage() {
        return "page/auth/register";
    }

    @PostMapping("/register")
    public String processRegister(
            @ModelAttribute RegisterRequestDto request,
            Model model,
            RedirectAttributes redirectAttributes
    ) {
        try {
            authService.register(request);

            redirectAttributes.addFlashAttribute("message", "회원가입이 완료되었습니다! 이메일 인증을 진행해주세요.");
            return "redirect:/auth/login";

        } catch (CustomException e) {
            log.warn("회원가입 실패: {}", e.getErrorCode().getMessage());
            model.addAttribute("errorMessage", e.getErrorCode().getMessage());
            return "page/auth/register";

        } catch (Exception e) {
            log.error("회원가입 시스템 오류", e);
            model.addAttribute("errorMessage", "시스템 오류가 발생했습니다.");
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