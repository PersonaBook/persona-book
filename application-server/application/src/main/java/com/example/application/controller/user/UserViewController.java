package com.example.application.controller.user;

import com.example.application.entity.User;
import com.example.application.util.JwtAuthUtil;
import jakarta.servlet.http.HttpServletRequest;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;

@Controller
public class UserViewController {

    @Autowired
    private JwtAuthUtil jwtAuthUtil;

    @GetMapping("/user/profile")
    public String getProfilePage(HttpServletRequest request, Model model) {
        model.addAttribute("title", "마이페이지");
        User user = jwtAuthUtil.getUserFromRequest(request);
        if (user == null) {
            model.addAttribute("errorMessage", "정보를 불러올 수 없습니다. 다시 로그인 해주세요.");
            return "page/profile";
        }
        model.addAttribute("user", user);
        return "page/profile";
    }
}
