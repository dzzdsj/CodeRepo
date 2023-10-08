package com.dzzdsj.demo.springdemo.ioc.LifeCycleOfBean.creation;

import org.springframework.beans.factory.BeanCreationException;
import org.springframework.beans.factory.InitializingBean;
import org.springframework.context.ApplicationContext;
import org.springframework.context.support.GenericXmlApplicationContext;

/**
 * 实现了InitializingBean接口后，xml就不需要指定init-method方法了，转而使用afterPropertiesSet方法
 */
public class UseInterface implements InitializingBean {
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
    @Override
    public void afterPropertiesSet() throws Exception {
        System.out.println("Initializing bean");
        if (name == null) {
            System.out.println("Using default name");
            name = DEFAULT_NAME;
        }
        if (age == Integer.MIN_VALUE) {
            throw new IllegalArgumentException("You must set the age property of any beans of type" +
                    UseInterface.class);
        }
    }

    public static UseInterface getBean(String beanName, ApplicationContext ctx) {
        try {
            UseInterface bean = (UseInterface) ctx.getBean(beanName);
            System.out.println(bean);
            return bean;
        } catch (BeanCreationException exception) {
            System.out.println("An error occured in bean configuration:" + exception.getMessage());
            return null;
        }
    }

    public static void main(String[] args) {
        GenericXmlApplicationContext ctx = new GenericXmlApplicationContext();
        ctx.load("classpath:ioc/LifeCycleOfBean/UseInitializingBean.xml");
        ctx.refresh();

        getBean("singerOne", ctx);
        getBean("singerTwo", ctx);
        getBean("singerThree", ctx);

        ctx.close();
    }
}
