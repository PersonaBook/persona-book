package com.example.application.exception;

import com.example.application.dto.auth.response.MessageResponse;
import jakarta.servlet.http.HttpServletRequest;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ControllerAdvice;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.servlet.ModelAndView;

import java.util.HashMap;
import java.util.Map;

@ControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(MethodArgumentNotValidException.class)
    public Object handleValidationExceptions(MethodArgumentNotValidException ex, HttpServletRequest request) {
        Map<String, String> errors = new HashMap<>();
        ex.getBindingResult().getAllErrors().forEach((error) -> {
            String fieldName = ((org.springframework.validation.FieldError) error).getField();
            String errorMessage = error.getDefaultMessage();
            errors.put(fieldName, errorMessage);
        });
        
        if (isApiRequest(request)) {
            return new ResponseEntity<>(new MessageResponse(HttpStatus.BAD_REQUEST, errors.toString()), HttpStatus.BAD_REQUEST);
        } else {
            ModelAndView mav = new ModelAndView("error/400");
            mav.addObject("message", "입력 데이터가 올바르지 않습니다.");
            mav.addObject("errors", errors);
            return mav;
        }
    }

    @ExceptionHandler(Exception.class)
    public Object globalExceptionHandler(Exception ex, HttpServletRequest request) {
        if (isApiRequest(request)) {
            MessageResponse message = new MessageResponse(HttpStatus.INTERNAL_SERVER_ERROR, ex.getMessage());
            return new ResponseEntity<>(message, HttpStatus.INTERNAL_SERVER_ERROR);
        } else {
            ModelAndView mav = new ModelAndView("error/500");
            mav.addObject("message", "서버 오류가 발생했습니다. 잠시 후 다시 시도해주세요.");
            mav.addObject("error", ex.getMessage());
            return mav;
        }
    }
    
    private boolean isApiRequest(HttpServletRequest request) {
        String requestURI = request.getRequestURI();
        String acceptHeader = request.getHeader("Accept");
        String contentType = request.getContentType();
        
        // API 경로로 시작하는 경우
        if (requestURI.startsWith("/api/")) {
            return true;
        }
        
        // AJAX 요청인 경우 (Accept 헤더에 application/json이 포함)
        if (acceptHeader != null && acceptHeader.contains("application/json")) {
            return true;
        }
        
        // Content-Type이 application/json인 경우
        if (contentType != null && contentType.contains("application/json")) {
            return true;
        }
        
        // X-Requested-With 헤더가 XMLHttpRequest인 경우 (AJAX)
        String requestedWith = request.getHeader("X-Requested-With");
        if ("XMLHttpRequest".equals(requestedWith)) {
            return true;
        }
        
        return false;
    }
}
