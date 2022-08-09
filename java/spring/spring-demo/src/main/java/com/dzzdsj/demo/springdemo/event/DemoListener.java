package com.dzzdsj.demo.springdemo.event;

import org.springframework.context.ApplicationListener;
import org.springframework.stereotype.Component;

/**
 * 事件监听器
 */
@Component
public class DemoListener implements ApplicationListener<DemoEvent> {
    public void onApplicationEvent(DemoEvent demoEvent) {
        String msg = demoEvent.getMsg();
        System.out.println("DemoListener 接收到 DemoEvent 发布的消息:" + msg);
    }
}
