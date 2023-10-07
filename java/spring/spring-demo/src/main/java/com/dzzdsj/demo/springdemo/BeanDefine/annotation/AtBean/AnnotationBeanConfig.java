package com.dzzdsj.demo.springdemo.BeanDefine.annotation.AtBean;

import lombok.Data;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
@Data
public class AnnotationBeanConfig {
    private Integer id;
    private String name;
    @Bean
    public AnnotationBeanConfig beanFoo(){
        AnnotationBeanConfig bean = new AnnotationBeanConfig();
        bean.setId(1);
        bean.setName("foo");
        return bean;
    }
}
