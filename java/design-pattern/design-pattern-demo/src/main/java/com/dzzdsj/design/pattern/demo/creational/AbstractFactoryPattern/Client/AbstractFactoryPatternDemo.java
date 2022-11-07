package com.dzzdsj.design.pattern.demo.creational.AbstractFactoryPattern.Client;

import com.dzzdsj.design.pattern.demo.creational.AbstractFactoryPattern.AbstractFactory.AbstractFactory;
import com.dzzdsj.design.pattern.demo.creational.AbstractFactoryPattern.AbstractProduct.AbstractProductA;
import com.dzzdsj.design.pattern.demo.creational.AbstractFactoryPattern.AbstractProduct.AbstractProductB;
import com.dzzdsj.design.pattern.demo.creational.AbstractFactoryPattern.AbstractFactory.FactoryProducer;

/**
 * 抽象工厂模式,
 */
public class AbstractFactoryPatternDemo {
    public static void main(String[] args) {
        AbstractFactory abstractFactoryA = FactoryProducer.getFactory("A");
        AbstractProductA abstractProductA1 = abstractFactoryA.createProductA("A1");
        AbstractProductA abstractProductA2 = abstractFactoryA.createProductA("A2");
        abstractProductA1.productAMethod();
        abstractProductA2.productAMethod();

        AbstractFactory abstractFactoryB = FactoryProducer.getFactory("B");
        AbstractProductB abstractProductB1 = abstractFactoryB.createProductB("B1");
        AbstractProductB abstractProductB2 = abstractFactoryB.createProductB("B2");
        abstractProductB1.productBMethod();
        abstractProductB2.productBMethod();

    }
}
