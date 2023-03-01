package com.dzzdsj.spring6.iocxml;

import com.dzzdsj.spring6.iocxml.inject.Book;
import com.dzzdsj.spring6.iocxml.inject.Emp;
import org.junit.jupiter.api.Test;
import org.springframework.context.ApplicationContext;
import org.springframework.context.support.ClassPathXmlApplicationContext;

public class TestDI {
    /**
     * setter方法注入测试
     */
    @Test
    public void testSetter() {
        ApplicationContext applicationContext = new ClassPathXmlApplicationContext("bean-di.xml");
        Book book = applicationContext.getBean("book", Book.class);
        System.out.println(book);
    }
    /**
     * 构造器注入测试
     */
    @Test
    public void testConstruct() {
        ApplicationContext applicationContext = new ClassPathXmlApplicationContext("bean-di.xml");
        Book book = applicationContext.getBean("bookCon", Book.class);
        System.out.println(book);
    }

    @Test
    public void testDI() {
        ApplicationContext applicationContext = new ClassPathXmlApplicationContext("bean-di.xml");
        Emp emp1 = applicationContext.getBean("emp1", Emp.class);
        System.out.println(emp1);

        Emp emp2 = applicationContext.getBean("emp2", Emp.class);
        System.out.println(emp2);

        Emp emp3 = applicationContext.getBean("emp3", Emp.class);
        System.out.println(emp3);

        Emp emp4 = applicationContext.getBean("emp4", Emp.class);
        System.out.println(emp4);
    }
}
