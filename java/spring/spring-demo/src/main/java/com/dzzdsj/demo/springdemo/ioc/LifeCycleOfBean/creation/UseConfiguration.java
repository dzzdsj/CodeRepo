package com.dzzdsj.demo.springdemo.ioc.LifeCycleOfBean.creation;

import org.springframework.beans.factory.BeanCreationException;
import org.springframework.context.ApplicationContext;
import org.springframework.context.annotation.AnnotationConfigApplicationContext;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Lazy;
import org.springframework.context.support.GenericApplicationContext;

/**
 * 使用 @Bean(initMethod="") 注解初始化bean
 */
public class UseConfiguration {
    private static final String DEFAULT_NAME = "Eric Clapton";
    private String name;
    private Integer age = Integer.MIN_VALUE;

    public void setName(String name) {
        this.name = name;
    }

    public void setAge(Integer age) {
        this.age = age;
    }

    @Override
    public String toString() {
        return "name:" + name + " age:" + age;
    }

    public void init() {
        System.out.println("Initializing bean");
        if (name == null) {
            System.out.println("Using default name");
            name = DEFAULT_NAME;
        }
        if (age == Integer.MIN_VALUE) {
            throw new IllegalArgumentException("You must set the age property of any beans of type" +
                    UseAnnotation.class);
        }
    }
    
    //内部配置类
    @Configuration
    static class BeanConfig{
        @Lazy
        @Bean(initMethod = "init")
        UseConfiguration singerOne() {
            UseConfiguration beanOne = new UseConfiguration();
            beanOne.setAge(39);
            return beanOne;
        }

        @Lazy
        @Bean(initMethod = "init")
        UseConfiguration singerTwo() {
            UseConfiguration beanTwo = new UseConfiguration();
            beanTwo.setName("John Mayer");
            return beanTwo;
        }

        @Lazy
        @Bean(initMethod = "init")
        UseConfiguration singerThree() {
            UseConfiguration beanThree = new UseConfiguration();
            beanThree.setName("John Mayer");
            beanThree.setAge(39);
            return beanThree;
        }
    }
    public static UseConfiguration getBean(String beanName, ApplicationContext ctx) {
        try {
            UseConfiguration bean = (UseConfiguration) ctx.getBean(beanName);
            System.out.println(bean);
            return bean;
        } catch (BeanCreationException exception) {
            System.out.println("An error occured in bean configuration:" + exception.getMessage());
            return null;
        }
    }
    public static void main(String[] args) {
        GenericApplicationContext ctx = new AnnotationConfigApplicationContext(BeanConfig.class);
        getBean("singerOne", ctx);
        getBean("singerTwo", ctx);
        getBean("singerThree", ctx);

        ctx.close();
    }

}
