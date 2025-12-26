package com.example.application.repository;

import com.example.application.entity.Book;
import com.example.application.entity.User;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;
import java.util.Optional;

public interface BookRepository extends JpaRepository<Book, Long> {
    List<Book> findByUser(User user);
    Optional<Book> findByBookIdAndUser(Long bookId, User user);
}
