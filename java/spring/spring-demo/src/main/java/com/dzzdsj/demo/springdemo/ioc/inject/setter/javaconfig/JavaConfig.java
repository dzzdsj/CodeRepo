package com.dzzdsj.demo.springdemo.ioc.inject.setter.javaconfig;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

//@Configuration
public class JavaConfig {
    @Bean
    public Computer computer() {
        Computer computer = new Computer();
        computer.setId(102);
        return computer;
    }

    @Bean
    public Cpu cpu() {
        Cpu cpu = new Cpu();
        cpu.setId(100);
        cpu.setName("abc");
        return cpu;
    }
}
