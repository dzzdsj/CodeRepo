package com.dzzdsj.demo.springdemo.ioc.inject.setter.javaconfig;

import lombok.ToString;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;

//@Component("computer")
@ToString
public class Computer {
    private int id;

//可以直接在属性上使用注解注入
//    @Autowired
    private Cpu cpu;

    public int getId() {
        return id;
    }

    public void setId(int id) {
        this.id = id;
    }

    public Cpu getCpu() {
        return cpu;
    }

//也可以在setter方法上使用注解注入
    @Autowired
    public void setCpu(Cpu cpu) {
        this.cpu = cpu;
    }
}
