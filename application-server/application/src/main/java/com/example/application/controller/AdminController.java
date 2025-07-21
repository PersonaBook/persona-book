package com.example.application.controller;

import com.example.application.service.UserService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;

import java.util.List;

@Controller
@RequestMapping("/admin")
public class AdminController {

    @Autowired
    private UserService userService;

    @GetMapping("/product/list")
    public String productList(Model model) {
        model.addAttribute("title", "상품 목록");
        return "admin/product_list";
    }

    @GetMapping("/product/register")
    public String productRegister(Model model) {
        model.addAttribute("title", "상품 등록");
        return "admin/product_register";
    }

    @GetMapping("/order/list")
    public String orderList(Model model) {
        model.addAttribute("title", "주문 목록");
        return "admin/order_list";
    }

    @GetMapping("/order/detail/{id}")
    public String orderDetail(@PathVariable("id") Long id, Model model) {
        model.addAttribute("title", "주문 상세");
        return "admin/order_detail";
    }

    @GetMapping("/member/list")
    public String memberList(Model model) {
        model.addAttribute("title", "회원 목록");
        List<com.example.application.entity.User> users = userService.getAllUsers();
        model.addAttribute("users", users);
        return "admin/member_list";
    }

    @GetMapping("/member/detail/{id}")
    public String memberDetail(@PathVariable("id") Long id, Model model) {
        model.addAttribute("title", "회원 상세");
        com.example.application.entity.User user = userService.getUserById(id);
        model.addAttribute("user", user);
        return "admin/member_detail";
    }

    @GetMapping("/stock/management")
    public String stockManagement(Model model) {
        model.addAttribute("title", "재고 관리");
        return "admin/stockManagement";
    }
}
