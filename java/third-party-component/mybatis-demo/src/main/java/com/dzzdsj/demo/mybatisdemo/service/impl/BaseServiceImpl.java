package com.dzzdsj.demo.mybatisdemo.service.impl;

import com.dzzdsj.demo.mybatisdemo.mapper.BaseMapper;
import com.dzzdsj.demo.mybatisdemo.service.BaseService;
import org.springframework.stereotype.Service;

import java.util.List;

@Service("baseService")
public class BaseServiceImpl implements BaseService {
    @Override
    public <T, K> List<T> queryByShardKeys(BaseMapper<T, K> baseMapper, List<K> shardKeys) {
        List<T> resultList = baseMapper.queryByShardKeys(shardKeys);
        return resultList;
    }
}
