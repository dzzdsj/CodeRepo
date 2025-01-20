package com.dzzdsj.demo.controller;

import com.dzzdsj.demo.entity.Test;
import com.dzzdsj.demo.service.TestService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
@RequestMapping("/test")
public class TestController {
    @Autowired
    private TestService testService;

    @GetMapping("/selectAll")
    public List<Test> selectAll(){
        return testService.selectAll();
    }
}
