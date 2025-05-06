package com.dzzdsj.demo.mybatisdemo.annotation.routemap;

public @interface EnableRouteMap {
    String targetTable();
    String[] mapKeys();
}
