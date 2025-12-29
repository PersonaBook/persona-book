package com.example.application.domain.user.controller;

import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;

@Controller
@RequiredArgsConstructor
public class UserViewController {
    @GetMapping("/user/profile")
    public String getProfilePage() {
        return "page/profile";
    }
}