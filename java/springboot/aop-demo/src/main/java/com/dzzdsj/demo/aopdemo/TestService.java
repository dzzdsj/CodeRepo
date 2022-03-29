package com.dzzdsj.demo.aopdemo;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

@Service
public class TestService {
    @Autowired
    private MyInterceptor myInterceptor;

    public void test(){
        System.out.println("enter service ");
    }
}
