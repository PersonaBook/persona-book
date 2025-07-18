package com.example.application.entity;

import jakarta.persistence.*;
import lombok.*;

import java.time.LocalDateTime;

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

    private String userName;
    private String userEmail;
    private String userPhoneNumber;
    private Integer userAge;
    private String userJob;

    @Column(columnDefinition = "TEXT")
    private String userSetting;

    private LocalDateTime createAt;
    private LocalDateTime updateAt;
}
