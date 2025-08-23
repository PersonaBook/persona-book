package com.example.application.controller.auth.view;

import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestParam;

@Controller
public class FindIdViewController {

    @GetMapping("/idInquiry")
    public String findIdView() {
        return "id-inquiry";
    }

    @GetMapping("/findIdSuccess")
    public String findIdSuccess(@RequestParam(value = "userId", required = false) String userId, Model model) {
        model.addAttribute("userId", userId);
        return "find-id-success";
    }

    @PostMapping("/find-id-success")
    public String findIdSuccess(Model model) {
        model.addAttribute("title", "아이디 찾기 완료");
        return "find-id-success";
    }
}
