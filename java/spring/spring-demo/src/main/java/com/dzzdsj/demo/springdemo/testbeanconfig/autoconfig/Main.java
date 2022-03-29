package com.dzzdsj.demo.springdemo.testbeanconfig.autoconfig;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.ApplicationContext;
import org.springframework.context.annotation.AnnotationConfigApplicationContext;
import org.springframework.context.annotation.ComponentScan;

/**
 * 在main方法中使用spring的bean
 */
@ComponentScan
public class Main {

    @Autowired
    private CDPlayer cdPlayer;

    public static void main(String[] args) {
        //不能使用new  ->java.lang.NullPointerException
        //详见https://blog.csdn.net/yzj99848873/article/details/45012193?utm_medium=distribute.pc_relevant.none-task-blog-2%7Edefault%7EBlogCommendFromMachineLearnPai2%7Edefault-1.base&depth_1-utm_source=distribute.pc_relevant.none-task-blog-2%7Edefault%7EBlogCommendFromMachineLearnPai2%7Edefault-1.base
//        Main main = new Main();
//        main.cdPlayer.play();

        ApplicationContext context =
                new AnnotationConfigApplicationContext(Main.class);
        System.out.println(context.containsBean("main")); //true
        System.out.println(context.containsBean("cdPlayer"));
        CDPlayer cdPlayer = context.getBean(CDPlayer.class);
        //todo 这个bean一直获取不到
        System.out.println(context.containsBean("cdPlayer"));
        System.out.println(context.containsBean("cDPlayer"));
        cdPlayer.play();
    }
}
