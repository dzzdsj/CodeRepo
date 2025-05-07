package com.dzzdsj.demo.mybatisdemo.service;

import com.dzzdsj.demo.mybatisdemo.mapper.BaseRouteMapMapper;

import java.util.List;

public interface BaseRouteMapService {
    <T,K> List<T> getShardkeys(BaseRouteMapMapper<T,K> routeMapMapper, K mapKey);
}
