package com.example.application.repository;

import com.example.application.entity.Question;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;

public interface QuestionRepository extends JpaRepository<Question, Long> {
    Optional<Question> findTopByUserIdAndBookIdOrderByCreatedAtDesc(Long userId, Long bookId);
}
