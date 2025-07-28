package com.example.application.controller.user;

import com.example.application.payload.response.MessageResponse;
import com.example.application.service.UserService;
import com.example.application.security.jwt.JwtTokenProvider;
import com.example.application.entity.User;
import com.example.application.repository.UserRepository;
import com.example.application.util.JwtAuthUtil;
import jakarta.servlet.http.HttpServletRequest;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@Controller
public class MyPageController {

    @Autowired
    private UserService userService;
    @Autowired
    private JwtTokenProvider jwtTokenProvider;
    @Autowired
    private UserRepository userRepository;
    @Autowired
    private JwtAuthUtil jwtAuthUtil;

    @GetMapping("/myPage")
    public String myPageView(HttpServletRequest request, Model model) {
        model.addAttribute("title", "마이페이지");
        User user = jwtAuthUtil.getUserFromRequest(request);
        if (user == null) {
            model.addAttribute("errorMessage", "정보를 불러올 수 없습니다. 다시 로그인 해주세요.");
            return "page/myPage";
        }
        model.addAttribute("user", user);
        return "page/myPage";
    }

    @PostMapping("/myPage/update")
    @ResponseBody
    public ResponseEntity<?> updateMyPage(HttpServletRequest request, @RequestParam(required = false) String userName,
                                          @RequestParam(required = false) String userEmail,
                                          @RequestParam(required = false) String userPhoneNumber,
                                          @RequestParam(required = false) String userBirthDate,
                                          @RequestParam(required = false) String userJob,
                                          @RequestParam(required = false) String otherUserJob) {
        User user = jwtAuthUtil.getUserFromRequest(request);
        if (user == null) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body(new MessageResponse(HttpStatus.UNAUTHORIZED, "인증이 필요합니다. 다시 로그인 해주세요."));
        }
        if (userName != null && !userName.isBlank()) user.setUserName(userName);
        if (userEmail != null && !userEmail.isBlank()) user.setUserEmail(userEmail);
        if (userPhoneNumber != null && !userPhoneNumber.isBlank()) user.setUserPhoneNumber(userPhoneNumber);
        if (userBirthDate != null && !userBirthDate.isBlank()) user.setUserBirthDate(java.time.LocalDate.parse(userBirthDate));
        if (userJob != null && !userJob.isBlank()) {
            if (userJob.equals("other") && otherUserJob != null && !otherUserJob.isBlank()) {
                user.setUserJob(otherUserJob);
            } else {
                user.setUserJob(userJob);
            }
        }
        userRepository.save(user);
        return ResponseEntity.ok(new MessageResponse(HttpStatus.OK, "회원정보가 성공적으로 수정되었습니다."));
    }
}

@RestController
@RequestMapping("/api")
class MyPageApiController {
    @Autowired
    private JwtAuthUtil jwtAuthUtil;

    @GetMapping("/myPage")
    public ResponseEntity<?> getMyPage(HttpServletRequest request) {
        User user = jwtAuthUtil.getUserFromRequest(request);
        if (user == null) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body("인증 필요");
        }
        Map<String, Object> result = new java.util.HashMap<>();
        result.put("userName", user.getUserName());
        result.put("userEmail", user.getUserEmail());
        result.put("userPhoneNumber", user.getUserPhoneNumber());
        result.put("userBirthDate", user.getUserBirthDate());
        result.put("userJob", user.getUserJob());
        result.put("userId", user.getUserId());
        return ResponseEntity.ok(result);
    }
}