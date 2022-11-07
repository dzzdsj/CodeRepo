package com.dzzdsj.design.pattern.demo.creational.BuilderPattern.Director;

import com.dzzdsj.design.pattern.demo.creational.BuilderPattern.Builder.Builder;

/**
 * 构造一个使用Builder接口的对象
 */
public class Director {
    private Builder builder;

    public Director(Builder builder) {
        this.builder = builder;
    }

    /**
     * 使用Builder对象的接口构建产品
     */
    public void constrcutProductA() {
        builder.buildPartA();
        builder.buildPartB();
    }

    public void constrcutProductB() {
        builder.buildPartB();
        builder.buildPartA();
    }
}
