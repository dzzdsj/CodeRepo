package com.dzzdsj.demo.mybatisdemo.annotation.routemap;

import java.lang.annotation.ElementType;
import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;
import java.lang.annotation.Target;

@Target({ElementType.TYPE,ElementType.METHOD})
@Retention(RetentionPolicy.RUNTIME)
public @interface RouteMap {
    String routeMapMethod() default "getShardkeys";
    Class<?> targetClass();
    String targetMethod() default "queryByShardKeys";
}
