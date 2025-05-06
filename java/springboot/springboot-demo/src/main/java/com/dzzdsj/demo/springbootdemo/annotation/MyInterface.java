package com.dzzdsj.demo.springbootdemo.annotation;

import org.springframework.stereotype.Component;

@Component("myInterface")
@MyAnnotation(name = "hehe")
public interface MyInterface {
    String test(String name);
}
