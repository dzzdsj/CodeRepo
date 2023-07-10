package com.dzzdsj.demo.mybatisdemo.mapper;

import com.dzzdsj.demo.mybatisdemo.entity.Student;


public interface StudentMapper {
    int deleteByPrimaryKey(Long sid);

    int insert(Student record);

    int insertSelective(Student record);

    Student selectByPrimaryKey(Long sid);

    int updateByPrimaryKeySelective(Student record);

    int updateByPrimaryKey(Student record);
}