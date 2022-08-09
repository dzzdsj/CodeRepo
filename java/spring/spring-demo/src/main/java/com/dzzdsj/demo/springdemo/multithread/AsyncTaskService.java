package com.dzzdsj.demo.springdemo.multithread;

import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Service;

/**
 * 异步任务执行类
 */
@Service
public class AsyncTaskService {
    //声明为异步方法，也可以注解在类上，表明该类的所有方法都是异步的
    @Async
    public void executeAsyncTask1() {
        System.out.println("executeAsyncTask1 ");
    }
    @Async
    public void executeAsyncTask2() {
        System.out.println("executeAsyncTask2 ");
    }
}
