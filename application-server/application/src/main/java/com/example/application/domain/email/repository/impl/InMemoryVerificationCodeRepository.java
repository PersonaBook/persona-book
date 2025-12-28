package com.example.application.domain.email.repository.impl;

import com.example.application.domain.email.repository.VerificationCodeRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.context.annotation.Profile;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

@Repository
@RequiredArgsConstructor
@Profile("dev")
public class InMemoryVerificationCodeRepository implements VerificationCodeRepository {

    private final Map<String, VerificationInfo> store = new ConcurrentHashMap<>();

    @Override
    public void save(String email, String code, int expiryMinutes) {
        store.put(email, new VerificationInfo(code, expiryMinutes));
    }

    @Override
    public String get(String email) {
        VerificationInfo info = store.get(email);
        if (info == null || !info.isValid()) {
            return null;
        }
        return info.code;
    }

    @Override
    public void remove(String email) {
        store.remove(email);
    }

    private static class VerificationInfo {
        private final String code;
        private final LocalDateTime expiryTime;

        public VerificationInfo(String code, int minutes) {
            this.code = code;
            this.expiryTime = LocalDateTime.now().plusMinutes(minutes);
        }

        public boolean isValid() {
            return LocalDateTime.now().isBefore(this.expiryTime);
        }
    }
}