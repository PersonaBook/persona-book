package com.example.application.controller.note;

import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;

@Controller
public class NoteController {

    @GetMapping("/note-main")
    public String noteMain(Model model) {
        model.addAttribute("title", "내 노트");
        return "page/noteMain";
    }

    @GetMapping("/noteDetail/{id}")
    public String noteDetail(@PathVariable Long id) {
        // In a real application, you would fetch note details using the ID
        return "page/noteDetail"; // Assuming you have a note_detail.html
    }
}