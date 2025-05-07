package com.dzzdsj.demo.mybatisdemo.annotation.routemap;

import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;

@Retention(RetentionPolicy.RUNTIME)
public @interface EnableRouteMap {
    String targetTable();
    String[] mapKeys();
}
