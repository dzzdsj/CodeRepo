package com.dzzdsj.demo.springdemo.ioc.beanoncondition;

import org.springframework.context.ApplicationContext;
import org.springframework.context.annotation.AnnotationConfigApplicationContext;

public class Main {
    public static void main(String[] args) {
        ApplicationContext applicationContext = new AnnotationConfigApplicationContext(BeanOnConditionConfig.class);
        DirectoryService directoryService = applicationContext.getBean(DirectoryService.class);
        System.out.println(applicationContext.getEnvironment().getProperty("os.name") + "系统下的命令为:" + directoryService.showDirectory());
    }
}
