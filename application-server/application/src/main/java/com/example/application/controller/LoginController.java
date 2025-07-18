package com.example.application.controller;

import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;

@Controller
public class LoginController {

    @GetMapping("/login")
    public static String  LoginView(String[] args) {

        return "page/login";
    }
}
