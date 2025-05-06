package com.dzzdsj.demo.mybatisdemo.annotation.routemap;

import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;

@Retention(RetentionPolicy.RUNTIME)
public @interface RouteMapMethod {
    String name() default "getShardkeys";
    Class<?> targetClass();
    String targetMethod() default "queryByShardKeys";
}
