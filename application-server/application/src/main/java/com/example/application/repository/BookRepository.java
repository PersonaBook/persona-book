package com.example.application.repository;

import com.example.application.entity.Book;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface BookRepository extends JpaRepository<Book, Long> {
    
    @Query("SELECT b FROM Book b WHERE b.userId = :userId AND b.deletedAt IS NULL ORDER BY b.createdAt ASC")
    List<Book> findByUserIdAndDeletedAtIsNull(@Param("userId") Long userId);
    
    @Query("SELECT b FROM Book b WHERE b.bookId = :bookId AND b.userId = :userId AND b.deletedAt IS NULL")
    Optional<Book> findByBookIdAndUserIdAndDeletedAtIsNull(@Param("bookId") Long bookId, @Param("userId") Long userId);
    
    @Query("SELECT b FROM Book b WHERE b.bookId = :bookId AND b.deletedAt IS NULL")
    Optional<Book> findByBookIdAndDeletedAtIsNull(@Param("bookId") Long bookId);
    
    @Query("SELECT b FROM Book b WHERE b.userId = :userId AND b.title = :title AND b.deletedAt IS NULL")
    Optional<Book> findByUserIdAndTitleAndDeletedAtIsNull(@Param("userId") Long userId, @Param("title") String title);
}