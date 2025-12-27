package com.example.application.domain.auth.repository;

import com.example.application.domain.auth.entity.VerificationToken;
import org.springframework.data.jpa.repository.JpaRepository;

public interface VerificationTokenRepository extends JpaRepository<VerificationToken, Long> {
    VerificationToken findByEmail(String email);
}
