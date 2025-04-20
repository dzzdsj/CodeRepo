package com.dzzdsj.demo.aopdemo.annotation;

import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;

@Retention(RetentionPolicy.RUNTIME)
public @interface AopAnnotation {
    String name() default "123";
}
