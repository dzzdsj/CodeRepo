package com.dzzdsj.design.pattern.demo.creational.BuilderPattern.Builder;

/**
 * 为创建一个Product对象的各个部件指定抽象接口
 */
public abstract class Builder {
    public abstract Builder buildPartA();

    public abstract Builder buildPartB();
}
