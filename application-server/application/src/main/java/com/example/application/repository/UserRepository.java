package com.example.application.repository;

import com.example.application.entity.User;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.Optional;

public interface UserRepository extends JpaRepository<User, Long> {
    Boolean existsByName(String name);
    Boolean existsByEmail(String email);
    Optional<User> findByEmail(String userEmail);
    Optional<User> findByNameAndEmail(String name, String email);
}
