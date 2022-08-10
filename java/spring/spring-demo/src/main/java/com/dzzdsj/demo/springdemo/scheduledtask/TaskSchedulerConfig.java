package com.dzzdsj.demo.springdemo.scheduledtask;

import org.springframework.context.annotation.ComponentScan;
import org.springframework.context.annotation.Configuration;
import org.springframework.scheduling.annotation.EnableScheduling;

@Configuration
@ComponentScan("com.dzzdsj.demo.springdemo.scheduledtask")
//@EnableScheduling 开启对计划任务的支持
@EnableScheduling
public class TaskSchedulerConfig {
}
