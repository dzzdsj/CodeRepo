package com.dzzdsj.demo.mybatisdemo.configuration;

public class RouteMapInfo {
    Class<?> routeMapperClass;
    String routeMapperMethod;
    Class<?> targetMapperClass;
    String targetMapperMethod;

    public Class<?> getRouteMapperClass() {
        return routeMapperClass;
    }

    public void setRouteMapperClass(Class<?> routeMapperClass) {
        this.routeMapperClass = routeMapperClass;
    }

    public String getRouteMapperMethod() {
        return routeMapperMethod;
    }

    public void setRouteMapperMethod(String routeMapperMethod) {
        this.routeMapperMethod = routeMapperMethod;
    }

    public Class<?> getTargetMapperClass() {
        return targetMapperClass;
    }

    public void setTargetMapperClass(Class<?> targetMapperClass) {
        this.targetMapperClass = targetMapperClass;
    }

    public String getTargetMapperMethod() {
        return targetMapperMethod;
    }

    public void setTargetMapperMethod(String targetMapperMethod) {
        this.targetMapperMethod = targetMapperMethod;
    }

    @Override
    public String toString() {
        return "RouteMapInfo{" +
                "routeMapperClass=" + routeMapperClass +
                ", routeMapperMethod='" + routeMapperMethod + '\'' +
                ", targetMapperClass=" + targetMapperClass +
                ", targetMapperMethod='" + targetMapperMethod + '\'' +
                '}';
    }
}
