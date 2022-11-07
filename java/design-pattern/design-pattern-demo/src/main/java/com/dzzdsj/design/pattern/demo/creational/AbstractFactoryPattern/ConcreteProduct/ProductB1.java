package com.dzzdsj.design.pattern.demo.creational.AbstractFactoryPattern.ConcreteProduct;

import com.dzzdsj.design.pattern.demo.creational.AbstractFactoryPattern.AbstractProduct.AbstractProductB;

/**
 * 具体产品对象
 */
public class ProductB1 implements AbstractProductB {
    @Override
    public void productBMethod() {
        System.out.println("My name is B1");
    }
}
