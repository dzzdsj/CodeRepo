package com.dzzdsj.demo.springdemo.ioc.BeanDefine.annotation.AtComponentScan;

import org.springframework.context.ApplicationContext;
import org.springframework.context.annotation.AnnotationConfigApplicationContext;
import org.springframework.context.annotation.ComponentScan;

@ComponentScan(basePackages = "com.dzzdsj.demo.springdemo.BeanDefine.annotation.AtComponentScan")
public class Main {
    public static void main(String[] args) {
        ApplicationContext applicationContext = new AnnotationConfigApplicationContext(Conf.class);
        ComponentBean componentBean = (ComponentBean) applicationContext.getBean("componentBean");
        System.out.println(componentBean);
    }
}
