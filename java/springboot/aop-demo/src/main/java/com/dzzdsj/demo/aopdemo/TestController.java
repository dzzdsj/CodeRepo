package com.dzzdsj.demo.aopdemo;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
class TestController {
    @Autowired
    private TestService testService;



    @GetMapping("test")
    public void test(){

        System.out.println("enter controller");
        testService.test();
        System.out.println("end");
    }
}
