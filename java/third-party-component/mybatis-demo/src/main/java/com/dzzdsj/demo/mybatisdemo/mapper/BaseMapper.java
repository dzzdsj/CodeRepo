package com.dzzdsj.demo.mybatisdemo.mapper;

import java.util.List;

public interface BaseMapper<T, K> {
    List<T> queryByShardKeys(List<K> shardKeys);
}
