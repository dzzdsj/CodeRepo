package com.dzzdsj.demo.springbootdemo;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

/**
 * 开启组件扫描和自动配置
 * @SpringBootApplication 整合了下列几大注释=
 * @SpringBootConfiguration (@Configuration) 使用spring基于java的配置+
 * @EnableAutoConfiguration 开启自动配置+
 * @ComponentScan 开启组件扫描。--组件被自动发现并注册为spring上下文里的bean。
 */
@SpringBootApplication
public class SpringbootDemoApplication {

    public static void main(String[] args) {
        /**
         * 负责启动引导应用程序
         */
        SpringApplication.run(SpringbootDemoApplication.class, args);
    }

}
