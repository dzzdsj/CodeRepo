package com.dzzdsj.design.pattern.demo.creational.AbstractFactoryPattern.Client;

import com.dzzdsj.design.pattern.demo.creational.AbstractFactoryPattern.AbstractFactory.AbstractFactory;
import com.dzzdsj.design.pattern.demo.creational.AbstractFactoryPattern.AbstractProduct.AbstractProductA;
import com.dzzdsj.design.pattern.demo.creational.AbstractFactoryPattern.AbstractProduct.AbstractProductB;
import com.dzzdsj.design.pattern.demo.creational.AbstractFactoryPattern.AbstractFactory.FactoryProducer;

/**
 * 抽象工厂模式
 * 意图：
 * 提供一个创建一系列相关或相互依赖的对象的接口，而无需指定具体的类
 * client类只操作抽象类（工厂、产品）的接口
 *
 * 适用性：
 * 当系统要独立它的产品的创建、组合和表示时
 * 当系统要由多个产品系列中的一个来配置时
 * 当要强调系列产品的相关性，以便联合使用时
 * 当提供的产品只想暴露接口，而不是实现时
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
