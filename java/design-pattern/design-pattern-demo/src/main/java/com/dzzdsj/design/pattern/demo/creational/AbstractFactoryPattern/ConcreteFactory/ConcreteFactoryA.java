package com.dzzdsj.design.pattern.demo.creational.AbstractFactoryPattern.ConcreteFactory;

import com.dzzdsj.design.pattern.demo.creational.AbstractFactoryPattern.AbstractFactory.AbstractFactory;
import com.dzzdsj.design.pattern.demo.creational.AbstractFactoryPattern.AbstractProduct.AbstractProductA;
import com.dzzdsj.design.pattern.demo.creational.AbstractFactoryPattern.AbstractProduct.AbstractProductB;
import com.dzzdsj.design.pattern.demo.creational.AbstractFactoryPattern.ConcreteProduct.ProductA1;
import com.dzzdsj.design.pattern.demo.creational.AbstractFactoryPattern.ConcreteProduct.ProductA2;

/**
 * 实现创建具体产品对象的操作
 */
public class ConcreteFactoryA extends AbstractFactory {
    @Override
    public AbstractProductB createProductB(String type) {
        return null;
    }

    @Override
    public AbstractProductA createProductA(String type) {
        if (type == null) {
            return null;
        }
        if (type.equalsIgnoreCase("A1")) {
            return new ProductA1();
        } else if (type.equalsIgnoreCase("A2")) {
            return new ProductA2();
        }
        return null;
    }
}
