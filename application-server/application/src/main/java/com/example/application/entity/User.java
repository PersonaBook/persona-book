package com.example.application.entity;

import jakarta.persistence.*;
import lombok.*;
import org.hibernate.annotations.CreationTimestamp;
import org.hibernate.annotations.UpdateTimestamp;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.HashSet;
import java.util.Set;

@Entity
@Table(name = "user")
@Getter @Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class User {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long userId;

    @Column(nullable = false, unique = true, length = 50)
    private String userName;

    @Column(nullable = false, unique = true, length = 100)
    private String userEmail;

    @Column(nullable = false, length = 15)
    private String userPhoneNumber;

    @Column(name = "user_birth_date")
    private LocalDate userBirthDate;

    @Column(name = "user_job")
    private String userJob;

    @Column(nullable = false)
    private String password;

    @Column(columnDefinition = "TEXT")
    private String userSetting;

    @CreationTimestamp
    private LocalDateTime createAt;

    @UpdateTimestamp
    private LocalDateTime updateAt;

    
}