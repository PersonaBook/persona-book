package com.example.application.dto.chat;

import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;

public class TestBCrypt {
    public static void main(String[] args) {
        String rawPassword = "tjejrdnjs1@";
        String encodedPassword = "$2a$10$OFCTtkhDmdHuT4mQ40LcauBKvOJlUtIkDbFCOSkryFeocHMXsOc52";
        BCryptPasswordEncoder encoder = new BCryptPasswordEncoder();
        System.out.println(encoder.matches(rawPassword, encodedPassword));
    }
}