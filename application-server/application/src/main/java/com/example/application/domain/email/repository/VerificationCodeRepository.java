package com.example.application.domain.email.repository;

public interface VerificationCodeRepository {
    void save(String email, String code, int expiryMinutes);
    String get(String email);
    void remove(String email);
}