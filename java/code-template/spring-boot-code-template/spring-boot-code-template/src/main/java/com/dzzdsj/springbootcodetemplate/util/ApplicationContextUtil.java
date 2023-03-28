package com.dzzdsj.springbootcodetemplate.util;

import org.springframework.beans.BeansException;
import org.springframework.context.ApplicationContext;
import org.springframework.context.ApplicationContextAware;
import org.springframework.stereotype.Component;

@Component
public class ApplicationContextUtil implements ApplicationContextAware {
    private static ApplicationContext applicationContext;

    @Override
    public void setApplicationContext(ApplicationContext applicationContext) throws BeansException {
        System.out.println("applicationContext正在初始化,application:" + applicationContext);
        this.applicationContext = applicationContext;
    }

    public static Object getBean(String name) {
        if (applicationContext == null) {
            System.out.println("applicationContext是空的");
        } else {
            System.out.println("applicationContext不是空的");
        }
        return applicationContext.getBean(name);
    }

    public static <T> T getBean(Class<T> clazz) {
        if (applicationContext == null) {
            System.out.println("applicationContext是空的");
        } else {
            System.out.println("applicationContext不是空的");
        }
        return applicationContext.getBean(clazz);
    }

    public static ApplicationContext getApplicationContext() {
        return applicationContext;
    }
}
