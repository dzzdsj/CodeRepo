package com.dzzdsj.demo.springbootdemo.annotation;

import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;

@Retention(RetentionPolicy.RUNTIME)
public @interface MyAnnotation {
    String name() default "dzzdsj";
}
