package com.dzzdsj.spring6.iocxml;

import com.dzzdsj.spring6.iocxml.inject.Book;
import org.junit.jupiter.api.Test;
import org.springframework.context.ApplicationContext;
import org.springframework.context.support.ClassPathXmlApplicationContext;

public class TestDependencyInject {
    @Test
    public void testSetter() {
        ApplicationContext applicationContext = new ClassPathXmlApplicationContext("bean-di.xml");
        Book book = applicationContext.getBean("book", Book.class);
        System.out.println(book);
    }

    @Test
    public void testConstruct() {
        ApplicationContext applicationContext = new ClassPathXmlApplicationContext("bean-di.xml");
        Book book = applicationContext.getBean("bookCon", Book.class);
        System.out.println(book);
    }
}
