package com.dzzdsj.demo.async;

import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Service;

import java.util.concurrent.TimeUnit;

import static com.dzzdsj.demo.async.TestController.lock;

@Service
public class AsyncService {

    @Async
    public void asyncMethod(){
        try {
            TimeUnit.MILLISECONDS.sleep(1000);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        System.out.println("enter asyncMethod");
    }

    @Async
    public void asyncMethod2(){
        try {
            TimeUnit.MILLISECONDS.sleep(1000);
            synchronized (lock){
                System.out.println("enter");
                lock.notifyAll();
            }
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        System.out.println("enter asyncMethod");
    }
}
