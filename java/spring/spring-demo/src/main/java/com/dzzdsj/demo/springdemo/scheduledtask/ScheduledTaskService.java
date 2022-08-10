package com.dzzdsj.demo.springdemo.scheduledtask;

import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Service;

import java.text.SimpleDateFormat;
import java.util.Date;

@Service
public class ScheduledTaskService {
    private static final SimpleDateFormat simpleDateFormat = new SimpleDateFormat("HH:mm:ss");
    // fixedRate 任务两次执行时间间隔是任务的开始点，而 fixedDelay 的间隔是前次任务的结束与下次任务的开始
    //以前我对 fixedRate 还有一个误区就是，以为任务时长超过 fixedRate 时会启动多个任务实例，其实不会;
    // 只不过会在上次任务执行完后立即启动下一轮。除非这个 Job 方法用 @Async 注解了，
    // 使得任务不在 TaskScheduler 线程池中执行，而是每次创建新线程来执行 --https://www.cnblogs.com/javahr/p/8318642.html
    @Scheduled(fixedRate = 5000)
    public void printCurrentTime() {
        System.out.println("现在的时间是:" + simpleDateFormat.format(new Date()));
    }
    @Scheduled(cron = "7 * * * * *")
    public void fixTimeExecution() {
        System.out.println("在指定的时间执行:" + simpleDateFormat.format(new Date()));
    }
}
