package com.example.application.global.security.interceptor;

import com.example.application.global.exception.CustomException;
import com.example.application.global.exception.ErrorCode;
import com.example.application.global.security.util.JwtProvider;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;
import org.springframework.web.servlet.HandlerInterceptor;

@Component
@RequiredArgsConstructor
public class AuthInterceptor implements HandlerInterceptor {

    private final JwtProvider jwtProvider;

    @Override
    public boolean preHandle(HttpServletRequest request, HttpServletResponse response, Object handler) {
        // Preflight 요청(OPTIONS)은 건너뜀 (CORS 이슈 방지)
        if (request.getMethod().equals("OPTIONS")) {
            return true;
        }

        // 토큰 추출
        String token = jwtProvider.resolveToken(request);

        // 토큰 유효성 검사
        // 토큰이 없거나, 위조되었거나, 만료되었다면 에러 발생
        if (token == null || !jwtProvider.isValidToken(token)) {
            throw new CustomException(ErrorCode.UNAUTHORIZED_USER);
        }

        // 토큰에서 userId(PK) 추출
        Long userId = jwtProvider.getUserId(token);

        // Controller로 userId 전달
        // 컨트롤러에서는 @RequestAttribute("userId") Long userId 로 꺼내 씀
        request.setAttribute("userId", userId);

        return true;
    }
}