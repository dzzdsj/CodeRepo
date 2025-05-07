package com.dzzdsj.demo.mybatisdemo.annotation.routemap;

import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;

@Retention(RetentionPolicy.RUNTIME)
public @interface RouteMapMapper {
    String targetTable();
    String[] mapKeys();
    Class<?> routeMapperClass();
}
