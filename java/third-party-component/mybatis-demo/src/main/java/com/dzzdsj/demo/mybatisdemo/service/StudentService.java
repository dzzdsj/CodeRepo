package com.dzzdsj.demo.mybatisdemo.service;

import com.dzzdsj.demo.mybatisdemo.annotation.routemap.RouteMapMapper;
import com.dzzdsj.demo.mybatisdemo.entity.Student;

import java.util.List;

public interface StudentService {
//    @RouteMapMapper(targetTable = "t_student", mapKeys = {"card_no", "sname"})//无效
    Student selectByPrimaryKey(Long sid);

    List<Student> findStudentsByCardNoAndName(String cardNo, String sname);
}
