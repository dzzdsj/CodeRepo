package com.dzzdsj.demo.springdemo.ioc.inject.setter.javaconfig;

import org.springframework.context.ApplicationContext;
import org.springframework.context.annotation.AnnotationConfigApplicationContext;

public class Main {
    public static void main(String[] args) {
        ApplicationContext applicationContext = new AnnotationConfigApplicationContext(JavaConfig.class);
        Cpu cpu = (Cpu) applicationContext.getBean("cpu", Cpu.class);
        System.out.println(cpu);
        Computer computer = (Computer) applicationContext.getBean(Computer.class);
        System.out.println(computer);
    }
}
