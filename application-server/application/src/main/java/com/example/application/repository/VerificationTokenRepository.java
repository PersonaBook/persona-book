package com.example.application.repository;

import com.example.application.entity.User;
import com.example.application.entity.VerificationToken;
import org.springframework.data.jpa.repository.JpaRepository;

public interface VerificationTokenRepository extends JpaRepository<VerificationToken, Long> {
    VerificationToken findByToken(String token);
    VerificationToken findByUser(User user);
    VerificationToken findByEmail(String email);
    void deleteByEmail(String email);
}
