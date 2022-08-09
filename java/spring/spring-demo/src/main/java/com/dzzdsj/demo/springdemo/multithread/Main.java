package com.dzzdsj.demo.springdemo.multithread;

import org.springframework.context.ApplicationContext;
import org.springframework.context.annotation.AnnotationConfigApplicationContext;

public class Main {
    public static void main(String[] args) {
        ApplicationContext applicationContext = new AnnotationConfigApplicationContext(TaskExecutorConfig.class);
        AsyncTaskService asyncTaskService = applicationContext.getBean(AsyncTaskService.class);
        for (int i = 0; i < 10; i++) {
            asyncTaskService.executeAsyncTask1();
            asyncTaskService.executeAsyncTask2();
        }
    }
}
/*executeAsyncTask2
executeAsyncTask2
executeAsyncTask2
executeAsyncTask1
executeAsyncTask1
executeAsyncTask1
executeAsyncTask1
executeAsyncTask2
executeAsyncTask1
executeAsyncTask1
executeAsyncTask2
executeAsyncTask1
executeAsyncTask2
executeAsyncTask1
executeAsyncTask2
executeAsyncTask1
executeAsyncTask2
executeAsyncTask1
executeAsyncTask2
executeAsyncTask2
*/