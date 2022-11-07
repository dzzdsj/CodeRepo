package com.dzzdsj.design.pattern.demo.creational.AbstractFactoryPattern.ConcreteProduct;

import com.dzzdsj.design.pattern.demo.creational.AbstractFactoryPattern.AbstractProduct.AbstractProductA;

/**
 * 具体产品对象
 */
public class ProductA1 implements AbstractProductA {
    @Override
    public void productAMethod() {
        System.out.println("I'm A1");
    }
}
