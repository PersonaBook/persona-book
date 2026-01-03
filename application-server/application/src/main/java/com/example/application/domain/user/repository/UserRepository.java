package com.example.application.domain.user.repository;

import com.example.application.domain.user.entity.User;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.Optional;

public interface UserRepository extends JpaRepository<User, Long> {
    Boolean existsByName(String name);
    Boolean existsByEmail(String email);
    Optional<User> findByEmail(String email);
    Optional<User> findByNameAndEmail(String name, String email);
    Optional<User> findByNameAndPhoneNumber(String name, String phoneNumber);
}
