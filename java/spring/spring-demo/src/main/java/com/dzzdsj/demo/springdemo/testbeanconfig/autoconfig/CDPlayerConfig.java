package com.dzzdsj.demo.springdemo.testbeanconfig.autoconfig;

import org.springframework.context.annotation.ComponentScan;
import org.springframework.context.annotation.Configuration;

/**
 *  注解@ComponentScan
 *  用于配置类,在Spring中启用组件扫描,默认会扫描与配置类相同的包。
 *  会扫描这个包以及这个包下的所有子包，查找带有@Component注解的类,在Spring中自动为其创建一个bean
 *
 *
 */
@Configuration
@ComponentScan
public class CDPlayerConfig {
}
