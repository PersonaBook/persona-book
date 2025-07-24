package com.example.application.controller;

import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;
import jakarta.servlet.http.HttpServletRequest;

@Controller
public class HomeViewController {

    @GetMapping({"/"})
    public String pdfMain(HttpServletRequest request, Model model) {
        System.out.println("=== 메인 페이지 요청 ===");
        String loginToken = (String) request.getSession().getAttribute("loginToken");
        System.out.println("세션 토큰: " + (loginToken != null ? "있음 - " + loginToken.substring(0, 20) + "..." : "없음"));
        if (loginToken != null) {
            System.out.println("토큰을 모델에 추가");
            model.addAttribute("loginToken", loginToken);
        }
        return "index";
    }
}