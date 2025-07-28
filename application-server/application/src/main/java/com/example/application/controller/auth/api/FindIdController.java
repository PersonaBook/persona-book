package com.example.application.controller.auth.api;

import com.example.application.dto.auth.response.MessageResponse;
import com.example.application.service.AuthService;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@Controller
public class FindIdController {

    private final AuthService authService;
    
    public FindIdController(AuthService authService) {
        this.authService = authService;
    }


    @PostMapping("/api/findId")
    @ResponseBody
    public ResponseEntity<?> findId(@RequestBody Map<String, String> request) {
        String email = request.get("email");
        if (email == null || email.isEmpty()) {
            return ResponseEntity.badRequest().body(new MessageResponse(HttpStatus.BAD_REQUEST, "Email is required."));
        }
        String username = authService.findUsernameByEmail(email);
        if (username != null) {
            return ResponseEntity.ok(new MessageResponse(HttpStatus.OK, "Your username is: " + username));
        } else {
            return ResponseEntity.status(HttpStatus.NOT_FOUND).body(new MessageResponse(HttpStatus.NOT_FOUND, "No user found with that email address."));
        }
    }
}