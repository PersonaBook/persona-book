package com.example.application.domain.email.repository.impl;

import com.example.application.domain.email.repository.VerificationCodeRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.context.annotation.Profile;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.stereotype.Repository;

import java.time.Duration;

@Repository
@Profile("prod")
@RequiredArgsConstructor
public class RedisVerificationCodeRepository implements VerificationCodeRepository {

    private final StringRedisTemplate redisTemplate;

    private static final String PREFIX = "email:verification:code:";

    @Override
    public void save(String email, String code, int expiryMinutes) {
        redisTemplate.opsForValue()
                .set(PREFIX + email, code, Duration.ofMinutes(expiryMinutes));
    }

    @Override
    public String get(String email) {
        return redisTemplate.opsForValue().get(PREFIX + email);
    }

    @Override
    public void remove(String email) {
        redisTemplate.delete(PREFIX + email);
    }
}