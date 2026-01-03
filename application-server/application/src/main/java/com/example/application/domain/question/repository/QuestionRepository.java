package com.example.application.domain.question.repository;

import com.example.application.domain.book.entity.Book;
import com.example.application.domain.question.entity.Question;
import com.example.application.domain.user.entity.User;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;

public interface QuestionRepository extends JpaRepository<Question, Long> {
    Optional<Question> findTopByUserAndBookOrderByCreatedAtDesc(User user, Book book);
}