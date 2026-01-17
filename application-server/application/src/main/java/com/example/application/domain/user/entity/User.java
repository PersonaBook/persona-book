package com.example.application.domain.user.entity;

import com.example.application.domain.user.dto.request.UserProfileUpdateRequestDto;
import com.example.application.global.common.entity.BaseTimeEntity;
import jakarta.persistence.*;
import lombok.*;
import org.springframework.util.StringUtils;

import java.time.LocalDate;

@Getter
@NoArgsConstructor
@AllArgsConstructor
@Builder
@Entity
@Table(name = "user")
public class User extends BaseTimeEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "user_id")
    private Long userId;

    @Column(nullable = false)
    private String password;

    @Column(nullable = false, unique = true, length = 50)
    private String name;

    @Column(nullable = false, unique = true, length = 100)
    private String email;

    @Column(nullable = false, length = 15)
    private String phoneNumber;

    @Column(name = "birth_date")
    private LocalDate birthDate;

    @Column(name = "job")
    private String job;

    // ─────────────── 비즈니스 메서드 (Setter 대체) ───────────────
    public void resetPassword(String newPassword) {
        this.password = newPassword;
    }

    public void updateProfile(UserProfileUpdateRequestDto request) {
        if (StringUtils.hasText(request.getName())) {
            this.name = request.getName();
        }

        if (StringUtils.hasText(request.getEmail())) {
            this.email = request.getEmail();
        }

        if (StringUtils.hasText(request.getPhoneNumber())) {
            this.phoneNumber = request.getPhoneNumber();
        }

        if (request.getBirthDate() != null) {
            this.birthDate = request.getBirthDate();
        }

        if (StringUtils.hasText(request.getJob())) {
            this.job = request.getJob();
        }
    }

    // ─────────────── 연관관계 (역방향) ───────────────
    // 역방향 매핑은 필요한 경우에만 사용
    // 데이터가 많아질 경우, 성능 저하
    // @Builder.Default
    // @OneToMany(mappedBy = "user", fetch = FetchType.LAZY)
    // private Set<Book> books = new HashSet<>();
    //
    // @Builder.Default
    // @OneToMany(mappedBy = "user", fetch = FetchType.LAZY)
    // private Set<Question> questions = new HashSet<>();
    //
    // @Builder.Default
    // @OneToMany(mappedBy = "user", fetch = FetchType.LAZY)
    // private Set<ChatHistory> chatHistories = new HashSet<>();
}
