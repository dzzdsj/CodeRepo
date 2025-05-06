package com.dzzdsj.demo.mybatisdemo.annotation.routemap;

import java.lang.annotation.ElementType;
import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;
import java.lang.annotation.Target;

@Retention(RetentionPolicy.RUNTIME)
public @interface RouteMapMapper {
    String targetTable();
    String[] mapKeys();
}
