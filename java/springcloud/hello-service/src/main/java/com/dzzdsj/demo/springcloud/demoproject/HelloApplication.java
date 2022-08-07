package com.dzzdsj.demo.springcloud.demoproject;

import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.builder.SpringApplicationBuilder;

@SpringBootApplication

public class HelloApplication {
    public static void main(String[] args) {
        new SpringApplicationBuilder(HelloApplication.class).web(true).run(args);
    }
}
