package com.dzzdsj.demo.springdemo.springtest;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Profile;

@Configuration
public class TestConfig {
    @Bean
    @Profile("dev")
    public TestBean devTestBean() {
        return new TestBean("dev bean");
    }

    @Bean
    @Profile("prod")
    public TestBean prodTestBean() {
        return new TestBean("prod bean");
    }
}
