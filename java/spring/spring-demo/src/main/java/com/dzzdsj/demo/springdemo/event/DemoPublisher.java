package com.dzzdsj.demo.springdemo.event;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.ApplicationContext;
import org.springframework.stereotype.Component;

/**
 * 事件发布类
 */
@Component
public class DemoPublisher {
    @Autowired
    ApplicationContext applicationContext;

    //使用applicationContext来发布事件
    public void publish(String msg) {
        applicationContext.publishEvent(new DemoEvent(this, msg));
    }
}
