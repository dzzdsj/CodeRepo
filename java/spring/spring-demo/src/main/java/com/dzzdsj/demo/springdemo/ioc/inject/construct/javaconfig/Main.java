package com.dzzdsj.demo.springdemo.ioc.inject.construct.javaconfig;

import org.springframework.context.ApplicationContext;
import org.springframework.context.annotation.AnnotationConfigApplicationContext;

public class Main {
    public static void main(String[] args) {
        ApplicationContext applicationContext = new AnnotationConfigApplicationContext(JavaConfig.class);
        System.out.println(applicationContext.getBean(Car.class));
    }
}
