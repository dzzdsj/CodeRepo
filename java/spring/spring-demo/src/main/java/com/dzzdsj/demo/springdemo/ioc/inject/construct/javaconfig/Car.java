package com.dzzdsj.demo.springdemo.ioc.inject.construct.javaconfig;

import lombok.ToString;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.DependsOn;

@ToString
//可以使用@DependsOn注解指定该Bean需要在指定的Bean生成之后生成
@DependsOn("window")
public class Car {
    private int id;
    private String name;
    private Window window;

//    @Autowired
    public Car(Window window) {
        this.window = window;
    }
}
