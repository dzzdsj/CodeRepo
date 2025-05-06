package com.dzzdsj.demo.springbootdemo.annotation;

import org.springframework.stereotype.Component;

//@Component("myClass")
@MyAnnotation(name = "dzzdsj")
public class MyClass implements MyInterface{
    @Override
    public String test(String name) {
        return null;
    }
}
