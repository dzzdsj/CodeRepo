package com.dzzdsj.demo.mybatisdemo.mapper;

import com.dzzdsj.demo.mybatisdemo.annotation.routemap.RouteMap;
import com.dzzdsj.demo.mybatisdemo.annotation.routemap.RouteMapMapper;

import java.util.List;

@RouteMapMapper(targetTable = "t_student", mapKeys = {"mobile"},routeMapperClass = MapStudentMobileMapper.class)
public interface MapStudentMobileMapper extends BaseRouteMapMapper<Long, String>{
    @RouteMap(targetClass = StudentMapper.class)
    List<Long> getShardkeys(String mapKey);
}
