package com.dzzdsj.demo.springdemo.ioc.inject.setter.xmlconfig;

import org.springframework.context.ApplicationContext;
import org.springframework.context.support.ClassPathXmlApplicationContext;

public class Main {
    public static void main(String[] args) {
        ApplicationContext applicationContext = new ClassPathXmlApplicationContext("classpath:ioc/inject/setter/setterinject.xml");
//----------------------setter注入-----------------------------------
        IDCard iDCard = (IDCard) applicationContext.getBean("iDCard");
        System.out.println(iDCard);
        iDCard.setCardNumber(99);
        Student student = (Student) applicationContext.getBean("student");
        System.out.println(student);
    }
}
