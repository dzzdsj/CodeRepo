package com.dzzdsj.demo.mybatisdemo;

import com.dzzdsj.demo.mybatisdemo.entity.Student;
import com.dzzdsj.demo.mybatisdemo.mapper.StudentMapper;
import jakarta.annotation.Resource;
import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;

import java.util.Date;

@SpringBootTest
public class StudentTest {
    @Resource
    private StudentMapper studentMapper;
//    int deleteByPrimaryKey(Long sid);

//    int insert(Student record){
//
//    }

    @Test
    void insertSelective(){
        Student student = new Student();
        student.setSid(1L);
        student.setSname("Tom");
        student.setAge(11);
        student.setCardNo("s0001");
        student.setMobile("13700000000");
        int result = studentMapper.insertSelective(student);
        System.out.println(result);
    }
//
//    Student selectByPrimaryKey(Long sid);
//
//    int updateByPrimaryKeySelective(Student record);
//
//    int updateByPrimaryKey(Student record);
}
