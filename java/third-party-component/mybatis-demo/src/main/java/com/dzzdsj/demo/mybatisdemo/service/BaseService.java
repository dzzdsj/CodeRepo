package com.dzzdsj.demo.mybatisdemo.service;

import com.dzzdsj.demo.mybatisdemo.mapper.BaseMapper;
import java.util.List;

public interface BaseService {
    <T,K> List<T> queryByShardKeys(BaseMapper<T,K> baseMapper, List<K> shardKeys);
}
