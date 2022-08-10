package com.dzzdsj.demo.springdemo.ioc.beanoncondition;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Conditional;
import org.springframework.context.annotation.Configuration;

/**
 * 基于条件的bean的创建，使用@Conditional注解
 */
@Configuration
public class BeanOnConditionConfig {
    @Bean
    //实例化符合条件的bean
    @Conditional(WindowsCondition.class)
    public DirectoryService windowsDirectory() {
        return new WindowsDirectoryServiceImpl();
    }

    @Bean
    @Conditional(LinuxCondition.class)
    public DirectoryService linuxDirectory() {
        return new LinuxDirectoryServiceImpl();
    }
}
