package com.example.application.controller;

import com.example.application.payload.request.SignupRequest;
import com.example.application.repository.UserRepository;
import com.example.application.service.AuthService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.ResponseBody;
import org.springframework.web.servlet.mvc.support.RedirectAttributes;

import java.util.Map;

@Controller
public class RegisterController {

    @Autowired
    private AuthService authService;

    @Autowired
    private UserRepository userRepository;

    @GetMapping("/register")
    public String registerView(Model model) {
        model.addAttribute("title", "회원가입");
        return "page/register";
    }

    @PostMapping("/register")
    public String register(SignupRequest signupRequest, Model model, RedirectAttributes redirectAttributes) {
        if (authService.registerUser(signupRequest)) {
            redirectAttributes.addFlashAttribute("message", "회원가입이 완료되었습니다! 이메일 인증을 진행해주세요.");
            return "redirect:index";
        } else {
            model.addAttribute("errorMessage", "회원가입에 실패했습니다. 사용자 이름 또는 이메일이 이미 존재합니다.");
            return "page/register";
        }
    }
}
