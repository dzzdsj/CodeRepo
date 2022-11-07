package com.dzzdsj.design.pattern.demo.creational.BuilderPattern;

import com.dzzdsj.design.pattern.demo.creational.BuilderPattern.ConcreteBuilder.ConcreteBuilder;
import com.dzzdsj.design.pattern.demo.creational.BuilderPattern.Director.Director;

/**
 * 建造者模式：组装具有复杂结构的实例
 */
public class Main {
    public static void main(String[] args) {
        ConcreteBuilder concreteBuilder = new ConcreteBuilder();
        Director director = new Director(concreteBuilder);
        director.constrcutProductA();
        concreteBuilder.getResult();
    }
}
