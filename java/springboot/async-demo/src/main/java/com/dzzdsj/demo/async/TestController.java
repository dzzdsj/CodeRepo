package com.dzzdsj.demo.async;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class TestController {
    public static final Object lock = new Object();

    @Autowired
    private AsyncService asyncService;

    /**
     * 调用异步方法
     */
    @GetMapping("/test")
    public void test(){
        System.out.println("hello");
        asyncService.asyncMethod();
        System.out.println("bye");
    }

    /**
     * 利用wait 和notifyAll 将异步转同步测试，这里需要持有同一个对象的锁
     */
    @GetMapping("/test2")
    public void test2(){
        System.out.println("hello");
        asyncService.asyncMethod2();
        synchronized (lock){
            try {
                lock.wait();
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }
        System.out.println("bye");
    }
}
