package com.dzzdsj.demo.springdemo.event;

import org.springframework.context.ApplicationContext;
import org.springframework.context.annotation.AnnotationConfigApplicationContext;

public class Main {
    public static void main(String[] args) {
        ApplicationContext applicationContext = new AnnotationConfigApplicationContext(EventConfig.class);
        DemoPublisher demoPublisher = applicationContext.getBean(DemoPublisher.class);
        demoPublisher.publish("hello world event");
    }
}
/*Connected to the target VM, address: '127.0.0.1:50340', transport: 'socket'
DemoListener 接收到 DemoEvent 发布的消息:hello world event
Disconnected from the target VM, address: '127.0.0.1:50340', transport: 'socket'

Process finished with exit code 0*/