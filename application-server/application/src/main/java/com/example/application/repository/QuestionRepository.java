package com.example.application.repository;

import com.example.application.entity.Book;
import com.example.application.entity.Question;
import com.example.application.entity.User;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;

public interface QuestionRepository extends JpaRepository<Question, Long> {
    Optional<Question> findTopByUserAndBookOrderByCreatedAtDesc(User user, Book book);
}