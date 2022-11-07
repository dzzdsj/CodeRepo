package com.dzzdsj.design.pattern.demo.creational.AbstractFactoryPattern.ConcreteFactory;

import com.dzzdsj.design.pattern.demo.creational.AbstractFactoryPattern.AbstractFactory.AbstractFactory;
import com.dzzdsj.design.pattern.demo.creational.AbstractFactoryPattern.AbstractProduct.AbstractProductA;
import com.dzzdsj.design.pattern.demo.creational.AbstractFactoryPattern.AbstractProduct.AbstractProductB;
import com.dzzdsj.design.pattern.demo.creational.AbstractFactoryPattern.ConcreteProduct.ProductB1;
import com.dzzdsj.design.pattern.demo.creational.AbstractFactoryPattern.ConcreteProduct.ProductB2;

/**
 * 实现创建具体产品对象的操作
 */
public class ConcreteFactoryB extends AbstractFactory {

    @Override
    public AbstractProductB createProductB(String type) {
        if (type == null) {
            return null;
        }
        if (type.equalsIgnoreCase("B1")) {
            return new ProductB1();
        } else if (type.equalsIgnoreCase("B2")) {
            return new ProductB2();
        }
        return null;
    }

    @Override
    public AbstractProductA createProductA(String type) {
        return null;
    }
}
