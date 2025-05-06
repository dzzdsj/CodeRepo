package com.dzzdsj.demo.mybatisdemo.controller;

import com.dzzdsj.demo.mybatisdemo.entity.Student;
import com.dzzdsj.demo.mybatisdemo.mapper.StudentMapper;
import com.dzzdsj.demo.mybatisdemo.service.StudentService;
import org.apache.ibatis.annotations.Param;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/student")
public class StudentController {
    @Autowired
    private StudentService studentService;

    @GetMapping("/find")
    public Student findStudent(@RequestParam Long sid){
        return studentService.selectByPrimaryKey(sid);
    }

    @GetMapping("/findByCardNoAndName")
    public List<Student> findByCardNoAndName(@RequestParam String cardNo, @RequestParam String sname){
        return studentService.findStudentsByCardNoAndName(cardNo, sname);
    }
}
