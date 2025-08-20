package com.example.application.repository;

import com.example.application.entity.Book;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;
import java.util.Optional;

public interface BookRepository extends JpaRepository<Book, Long> {
    List<Book> findByUser_UserIdAndDeletedAtIsNull(Long userId);
    Optional<Book> findByBookIdAndUser_UserIdAndDeletedAtIsNull(Long bookId, Long userId);
}
