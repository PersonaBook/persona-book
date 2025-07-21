package com.example.application.controller;

import com.example.application.service.PdfService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.core.io.Resource;
import org.springframework.core.io.UrlResource;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;
import com.example.application.payload.response.MessageResponse;
import com.example.application.util.JwtAuthUtil;
import com.example.application.entity.User;
import jakarta.servlet.http.HttpServletRequest;
import java.io.File;
import java.nio.file.Path;
import java.nio.file.Paths;

@Controller
public class PdfController {

    @Autowired
    private PdfService pdfService;

    @Autowired
    private JwtAuthUtil jwtAuthUtil;

    @GetMapping({"/", "/pdf-main"})
    public String pdfMain() {
        return "page/pdfMain";
    }

    @GetMapping("/pdfDetail")
    public String pdfDetail() {
        return "page/pdfDetail";
    }

    @PostMapping("/api/pdf/upload")
    @ResponseBody
    public ResponseEntity<?> uploadPdf(@RequestParam("file") MultipartFile file, HttpServletRequest request) {
        User user = jwtAuthUtil.getUserFromRequest(request);
        if (user == null) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body("인증 필요");
        }
        String email = user.getUserEmail();
        String userPdfDir = "src/main/resources/static/pdf/" + email;
        File dir = new File(userPdfDir);
        if (!dir.exists()) dir.mkdirs();

        String filename = file.getOriginalFilename();
        File dest = new File(dir, filename);
        try {
            file.transferTo(dest);
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body("PDF 저장 실패: " + e.getMessage());
        }
        return ResponseEntity.ok("PDF 업로드 성공: " + filename);
    }

    @GetMapping("/api/pdf/view/{filename}")
    @ResponseBody
    public ResponseEntity<Resource> viewPdf(@PathVariable String filename, HttpServletRequest request) {
        User user = jwtAuthUtil.getUserFromRequest(request);
        if (user == null) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).build();
        }
        String email = user.getUserEmail();
        Path filePath = Paths.get("src/main/resources/static/pdf/" + email + "/" + filename);
        try {
            Resource resource = new UrlResource(filePath.toUri());
            if (!resource.exists()) return ResponseEntity.notFound().build();
            return ResponseEntity.ok()
                .header(HttpHeaders.CONTENT_DISPOSITION, "inline; filename=\"" + filename + "\"")
                .body(resource);
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }
}