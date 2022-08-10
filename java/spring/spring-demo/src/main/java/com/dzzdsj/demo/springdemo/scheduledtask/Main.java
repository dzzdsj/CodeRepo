package com.dzzdsj.demo.springdemo.scheduledtask;

import org.springframework.context.ApplicationContext;
import org.springframework.context.annotation.AnnotationConfigApplicationContext;

public class Main {
    public static void main(String[] args) {
        ApplicationContext applicationContext = new AnnotationConfigApplicationContext(TaskSchedulerConfig.class);
    }
}
