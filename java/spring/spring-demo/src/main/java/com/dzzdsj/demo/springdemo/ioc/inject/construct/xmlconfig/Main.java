package com.dzzdsj.demo.springdemo.ioc.inject.construct.xmlconfig;

import org.springframework.context.ApplicationContext;
import org.springframework.context.support.ClassPathXmlApplicationContext;

public class Main {
    public static void main(String[] args) {
        ApplicationContext applicationContext = new ClassPathXmlApplicationContext("classpath:ioc/inject/construct/constructinject.xml");
//----------------------构造函数注入-----------------------------------
        House house = (House) applicationContext.getBean("house");
        System.out.println(house);
        Door door = (Door) applicationContext.getBean("door");
        System.out.println(door);
    }
}
