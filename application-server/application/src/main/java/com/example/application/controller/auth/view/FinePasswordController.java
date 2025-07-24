package com.example.application.controller.auth.view;

import org.springframework.web.bind.annotation.GetMapping;

public class FinePasswordController {

    @GetMapping("/pwInquiry")
    public String findPasswordView() {
        return "user/pwInquiry";
    }

    @GetMapping("/findPasswordSuccess")
    public String findPasswordSuccess() {
        return "page/findPasswordSuccess";
    }
}
