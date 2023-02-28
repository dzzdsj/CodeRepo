package com.dzzdsj.spring6.iocxml;

import com.dzzdsj.spring6.iocxml.getbean.User;
import com.dzzdsj.spring6.iocxml.getbean.UserDao;
import org.junit.jupiter.api.Test;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.context.ApplicationContext;
import org.springframework.context.support.ClassPathXmlApplicationContext;

public class TestGetBean {
    private Logger logger = LoggerFactory.getLogger(TestGetBean.class);

    /**
     * 根据id获取bean
     */
    @Test
    public void testGetBeanById() {
        ApplicationContext context = new ClassPathXmlApplicationContext("bean.xml");
        User user = (User) context.getBean("user");
        System.out.println("1:" + user);
        user.run();
        logger.info("hello");
        logger.trace("hello");
    }
    /**
     * 根据类型获取bean
     */
    @Test
    public void testGetBeanByType() {
        ApplicationContext context = new ClassPathXmlApplicationContext("bean.xml");
        User user = (User) context.getBean(User.class);
        System.out.println("1:" + user);
        user.run();
    }

    /**
     * 根据id和类型获取bean
     */
    @Test
    public void testGetBeanByIdAndType() {
        ApplicationContext context = new ClassPathXmlApplicationContext("bean.xml");
        User user = (User) context.getBean("user",User.class);
        System.out.println("1:" + user);
        user.run();
    }

    /**
     * 根据id和类型获取bean
     */
    @Test
    public void testGetBeanByInterface() {
        ApplicationContext context = new ClassPathXmlApplicationContext("bean.xml");
        UserDao userDao = (UserDao) context.getBean(UserDao.class);
        System.out.println("1:" + userDao);

    }
}
