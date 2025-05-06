package com.dzzdsj.demo.mybatisdemo.mapper;

import com.dzzdsj.demo.mybatisdemo.annotation.ClassAnnotation;
import com.dzzdsj.demo.mybatisdemo.annotation.MethodAnnotation;
import com.dzzdsj.demo.mybatisdemo.entity.Student;
import org.apache.ibatis.annotations.Param;

import java.util.List;


@ClassAnnotation(value = "studentMapper")
//@RouteMapMapper(targetTable = "t_student", mapKeys = {"card_no", "sname"})//无效
public interface StudentMapper {
    int deleteByPrimaryKey(Long sid);

    int insert(Student record);

    int insertSelective(Student record);

    @MethodAnnotation(value = "selectByPrimaryKey")
    Student selectByPrimaryKey(@Param("sid") Long sid);

    List<Student> selectByCardNoAndName(@Param("cardNo") String cardNo, @Param("sname") String sname);
    int updateByPrimaryKeySelective(Student record);

    int updateByPrimaryKey(Student record);
}