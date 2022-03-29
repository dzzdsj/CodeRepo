package com.dzzdsj.demo.javaadvance.javaSE.annotation;

import java.lang.annotation.*;

/**
 * 参考：https://blog.csdn.net/xsp_happyboy/article/details/80987484
 */
//几个常用的元注解
@Inherited //是指定某个自定义注解如果写在了父类的声明部分，那么子类的声明部分也能自动拥有该注解。@Inherited注解只对那些@Target被定义为ElementType.TYPE的自定义注解起作用
@Documented //是被用来指定自定义注解是否能随着被定义的java文件生成到JavaDoc文档当中
@Retention(RetentionPolicy.RUNTIME)//注解生效的范围，三个阶段：1、Java源文件阶段；2、编译到class文件阶段；3、运行期阶段
@Target({ElementType.METHOD, ElementType.TYPE})//注解可使用的地方
public @interface MyAnnotation {
    //元素的类型只能是基本数据类型、String、Class、枚举类型、注解类型（体现了注解的嵌套效果）以及上述类型的一位数组
    //属性是带括号的
    String name();
    int age() default 18;   //没默认值的属性使用时必须赋值
    int[] score();
}
