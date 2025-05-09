package com.dzzdsj.demo.mybatisdemo.service.impl;

import com.dzzdsj.demo.mybatisdemo.mapper.BaseRouteMapMapper;
import com.dzzdsj.demo.mybatisdemo.service.BaseRouteMapService;
import org.springframework.stereotype.Service;

import java.util.List;
@Service("baseRouteMapService")
public class BaseRouteMapServiceImpl implements BaseRouteMapService {
    @Override
    public <T, K> List<T> getShardkeys(BaseRouteMapMapper baseRouteMapMapper, K mapKey) {
        List<T> shardkeys = baseRouteMapMapper.getShardkeys(mapKey);
        return shardkeys;
    }
}
