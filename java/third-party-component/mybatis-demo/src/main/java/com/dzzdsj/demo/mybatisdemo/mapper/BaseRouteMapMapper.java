package com.dzzdsj.demo.mybatisdemo.mapper;

import java.util.List;

public interface BaseRouteMapMapper<T, K> {
    List<T> getShardkeys(K mapKey);
}
