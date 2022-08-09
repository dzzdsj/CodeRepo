package com.dzzdsj.demo.springdemo.ioc.inject.construct.javaconfig;

import lombok.ToString;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.DependsOn;
import org.springframework.stereotype.Component;

@ToString
//可以使用@DependsOn注解指定该Bean需要在指定的Bean生成之后生成
@DependsOn("window")
//@Component注解的类会被@ComponentScan注解的配置类扫描到并注册为Bean
@Component("car")
public class Car {
    @Value("100")
    private int id;
    private String name;
    @Autowired
    private Window window;

//    @Autowired
//    public Car(Window window) {
//        this.window = window;
//    }
}
