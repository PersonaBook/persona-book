package com.example.application.controller;

import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;

@Controller
public class index {

    @GetMapping("/")
    public static String main(String[] args) {

        return "page/pdfMain";

    }
}
