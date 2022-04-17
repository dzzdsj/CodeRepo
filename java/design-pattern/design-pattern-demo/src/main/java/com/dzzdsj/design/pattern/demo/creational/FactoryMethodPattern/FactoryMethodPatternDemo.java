package com.dzzdsj.design.pattern.demo.creational.FactoryMethodPattern;

import com.dzzdsj.design.pattern.demo.creational.FactoryMethodPattern.ConcreteCreator.ConcreteFactoryA;
import com.dzzdsj.design.pattern.demo.creational.FactoryMethodPattern.Creator.IFactory;

public class FactoryMethodPatternDemo {
    public static void main(String[] args) {
        IFactory factoryA = new ConcreteFactoryA();
        IFactory factoryB = new ConcreteFactoryA();
        factoryA.createProduct();
        factoryB.createProduct();

    }
}
