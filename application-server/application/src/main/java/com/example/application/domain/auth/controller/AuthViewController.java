package com.example.application.domain.auth.controller;

import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;

@Controller
@RequestMapping("/auth")
public class AuthViewController {

    @GetMapping("/login")
    public String getLoginPage() {
        return "page/auth/login";
    }

    @GetMapping("/register")
    public String getRegisterPage() {
        return "page/auth/register";
    }

    @GetMapping("/id/find")
    public String getIdFindPage() {
        return "page/auth/id-find";
    }

    @GetMapping("/id/find/success")
    public String getIdFindSuccessPage() {
        return "page/auth/id-find-success";
    }

    @GetMapping("/password/reset")
    public String getPasswordResetPage() {
        return "page/auth/password-reset";
    }

    @GetMapping("/password/reset/success")
    public String getPasswordResetSuccessPage() {
        return "page/auth/password-reset-success";
    }
}