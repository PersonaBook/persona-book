package com.example.application.domain.user.controller;

import com.example.application.domain.user.dto.response.UserProfileResponseDto;
import com.example.application.domain.user.service.UserService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestAttribute;

@Controller
@RequiredArgsConstructor // 생성자 주입 (Autowired 제거)
public class UserViewController {

    private final UserService userService;

    @GetMapping("/user/profile")
    public String getProfilePage(
            @RequestAttribute("userId") Long userId,
            Model model
    ) {
        UserProfileResponseDto userProfile = userService.getUserProfile(userId);
        model.addAttribute("user", userProfile);

        return "page/profile";
    }
}