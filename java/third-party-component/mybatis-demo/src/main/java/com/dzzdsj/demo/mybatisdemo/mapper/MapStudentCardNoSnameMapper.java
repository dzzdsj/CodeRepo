package com.dzzdsj.demo.mybatisdemo.mapper;

import com.dzzdsj.demo.mybatisdemo.annotation.routemap.RouteMapMapper;

import java.util.List;

@RouteMapMapper(targetTable = "t_student", mapKeys = {"card_no", "sname"})
public interface MapStudentCardNoSnameMapper {
    List<String> getShardkeys(String mapKey);
}
