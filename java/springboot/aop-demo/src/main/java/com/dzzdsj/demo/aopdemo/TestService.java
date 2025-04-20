package com.dzzdsj.demo.aopdemo;

import com.dzzdsj.demo.aopdemo.annotation.AopAnnotation;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

@Service
public class TestService {
    @Autowired
    private MyInterceptor myInterceptor;

    @AopAnnotation(name = "456")
    public void test(){
        System.out.println("enter service ");
    }
}
