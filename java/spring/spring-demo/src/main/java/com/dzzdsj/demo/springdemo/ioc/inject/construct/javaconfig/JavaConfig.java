package com.dzzdsj.demo.springdemo.ioc.inject.construct.javaconfig;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class JavaConfig {
    @Bean
    public Car car() {
        Car car = new Car(this.window());
        return car;
    }

    @Bean
    public Window window() {
        Window window = new Window();
        window.setId(100);
        window.setName("abd");
        return window;
    }
}
