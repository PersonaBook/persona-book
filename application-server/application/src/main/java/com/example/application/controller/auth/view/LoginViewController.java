package com.example.application.controller.auth.view;

import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;

@Controller
public class LoginViewController {

    @GetMapping("/login")
    public String loginView(Model model) {

        model.addAttribute("title", "로그인");
        return "page/login";
    }
}