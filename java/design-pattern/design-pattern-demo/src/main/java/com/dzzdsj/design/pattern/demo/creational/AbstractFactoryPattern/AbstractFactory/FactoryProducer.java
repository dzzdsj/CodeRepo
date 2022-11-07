package com.dzzdsj.design.pattern.demo.creational.AbstractFactoryPattern.AbstractFactory;

import com.dzzdsj.design.pattern.demo.creational.AbstractFactoryPattern.ConcreteFactory.ConcreteFactoryA;
import com.dzzdsj.design.pattern.demo.creational.AbstractFactoryPattern.ConcreteFactory.ConcreteFactoryB;

/**
 * 工厂生成器类，通过入参获取对应的工厂。
 */
public class FactoryProducer {
    public static AbstractFactory getFactory(String factoryType) {
        if (factoryType.equalsIgnoreCase("A")) {
            return new ConcreteFactoryA();
        } else if (factoryType.equalsIgnoreCase("B")) {
            return new ConcreteFactoryB();
        }
        return null;
    }
}
