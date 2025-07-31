package com.example.application.repository;

import com.example.application.entity.User;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.Optional;

public interface UserRepository extends JpaRepository<User, Long> {
    Boolean existsByUserName(String userName);
    Boolean existsByUserEmail(String userEmail);
    Optional<User> findByUserEmail(String userEmail);
}
