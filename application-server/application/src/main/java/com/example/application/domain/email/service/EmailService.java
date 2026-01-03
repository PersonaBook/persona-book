package com.example.application.domain.email.service;

import com.example.application.domain.email.repository.VerificationCodeRepository;
import com.example.application.global.exception.CustomException;
import com.example.application.global.exception.ErrorCode;
import jakarta.mail.MessagingException;
import jakarta.mail.internet.MimeMessage;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.mail.javamail.JavaMailSender;
import org.springframework.mail.javamail.MimeMessageHelper;
import org.springframework.stereotype.Service;

import java.security.SecureRandom;

@Service
@Slf4j
@RequiredArgsConstructor
public class EmailService {

    private final JavaMailSender javaMailSender;

    private final VerificationCodeRepository verificationCodeRepository;

    private static final SecureRandom secureRandom = new SecureRandom();
    private static final int VERIFICATION_CODE_EXPIRY_MINUTES = 5;

    public void sendVerificationCode(String email) {
        String verificationCode = createVerificationCode();

        verificationCodeRepository.save(email, verificationCode, VERIFICATION_CODE_EXPIRY_MINUTES);

        try {
            String to = email;
            String subject = "이메일 인증 코드";
            String text = verificationCode;

            sendEmail(to, subject, text);

            log.info("이메일 발송 성공: {}", email);
        } catch (Exception e) {
            verificationCodeRepository.remove(email);
            log.error("이메일 발송 실패: {}", email, e);
            throw new CustomException(ErrorCode.EMAIL_SEND_FAILED);
        }
    }

    public void verifyCode(String email, String inputCode) {
        String savedVerificationCode = verificationCodeRepository.get(email);

        if (savedVerificationCode == null || !savedVerificationCode.equals(inputCode)) {
            throw new CustomException(ErrorCode.INVALID_AUTH_CODE);
        }

        verificationCodeRepository.remove(email);
        log.info("이메일 인증 성공: {}", email);
    }

    private void sendEmail(String to, String subject, String text) {
        MimeMessage message = javaMailSender.createMimeMessage();
        try {
            MimeMessageHelper helper = new MimeMessageHelper(message, false, "UTF-8");
            helper.setTo(to);
            helper.setSubject(subject);
            helper.setText(text, true);
            javaMailSender.send(message);
        } catch (MessagingException e) {
            throw new RuntimeException(e);
        }
    }

    private String createVerificationCode() {
        int code = 100000 + secureRandom.nextInt(900000);
        return String.valueOf(code);
    }
}