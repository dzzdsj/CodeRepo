package com.dzzdsj.demo.springdemo.ioc.BeanDefine.annotation.AtBean;

import org.springframework.context.ApplicationContext;
import org.springframework.context.annotation.AnnotationConfigApplicationContext;

public class Main {
    public static void main(String[] args) {
        ApplicationContext applicationContext = new AnnotationConfigApplicationContext(AnnotationBeanConfig.class);
        AnnotationBeanConfig annotationBeanConfig = (AnnotationBeanConfig) applicationContext.getBean("annotationBeanConfig");
        AnnotationBeanConfig beanFoo = (AnnotationBeanConfig) applicationContext.getBean("beanFoo");
        System.out.println(beanFoo);
        System.out.println(annotationBeanConfig);
    }
}
