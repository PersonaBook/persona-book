package com.example.application.domain.book.repository;

import com.example.application.domain.book.entity.Book;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;
import java.util.Optional;

public interface BookRepository extends JpaRepository<Book, Long> {
    List<Book> findAllByUser_UserId(Long userId);
    Optional<Book> findByBookIdAndUser_UserId(Long bookId, Long userId);
}
