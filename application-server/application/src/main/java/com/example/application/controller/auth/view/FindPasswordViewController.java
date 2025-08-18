package com.example.application.controller.auth.view;

import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;

@Controller
public class FindPasswordViewController {

    @GetMapping("/pwInquiry")
    public String findPasswordView() {
        return "pw-inquiry";
    }

    @GetMapping("/findPasswordSuccess")
    public String findPasswordSuccess() {
        return "find-password-success";
    }
}
