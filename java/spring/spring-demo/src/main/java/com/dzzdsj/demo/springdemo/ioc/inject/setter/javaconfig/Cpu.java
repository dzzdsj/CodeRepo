package com.dzzdsj.demo.springdemo.ioc.inject.setter.javaconfig;

import lombok.ToString;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.context.annotation.Bean;
import org.springframework.stereotype.Component;

//@Component(value = "cpu")
@ToString
public class Cpu {
    private int id;
    private String name;

//    @Bean
//    public Cpu cpu(){
//        return new Cpu();
//    }


    public int getId() {
        return id;
    }

    public void setId(int id) {
        this.id = id;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }
}
