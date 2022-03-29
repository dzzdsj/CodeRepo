package com.dzzdsj.design.pattern.demo.DesignPatternRunoobDemo.BuilderPattern;

//定义食物的接口
public interface Item {
    String name();

    Packing packing();

    double price();
}
