package com.dzzdsj.demo.springdemo.ioc.BeanDefine.annotation.AtComponentScan;

import lombok.Data;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;


@Data
public class ComponentBean {
    private Integer id;
    private String name;
}
