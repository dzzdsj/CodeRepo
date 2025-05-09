package com.dzzdsj.demo.mybatisdemo.service.impl;

import com.dzzdsj.demo.mybatisdemo.annotation.routemap.EnableRouteMap;
import com.dzzdsj.demo.mybatisdemo.entity.Student;
import com.dzzdsj.demo.mybatisdemo.mapper.StudentMapper;
import com.dzzdsj.demo.mybatisdemo.service.StudentService;
import jakarta.annotation.Resource;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class StudentServiceImpl implements StudentService {
    @Resource
    private StudentMapper studentMapper;
    @Override
    public Student selectByPrimaryKey(Long sid) {
        return studentMapper.selectByPrimaryKey(sid);
    }
    @Override
    @EnableRouteMap(targetTable = "t_student", mapKeys = {"card_no", "sname"})
    public List<Student> findStudentsByCardNoAndName(String cardNo, String sname) {
        return studentMapper.selectByCardNoAndName(cardNo, sname);
    }
    @Override
    @EnableRouteMap(targetTable = "t_student", mapKeys = {"mobile"})
    public List<Student> findByMobile(String mobile) {
        return studentMapper.selectByMobile(mobile);
    }
}
