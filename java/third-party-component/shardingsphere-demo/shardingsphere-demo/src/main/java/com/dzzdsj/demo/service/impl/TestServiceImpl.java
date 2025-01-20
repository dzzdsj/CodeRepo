package com.dzzdsj.demo.service.impl;

import com.dzzdsj.demo.dao.TestDao;
import com.dzzdsj.demo.entity.Test;
import com.dzzdsj.demo.service.TestService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;
@Service
public class TestServiceImpl implements TestService {
    @Autowired
    private TestDao testDao;
    @Override
    public List<Test> selectAll() {
        return testDao.findAll();
    }
}
