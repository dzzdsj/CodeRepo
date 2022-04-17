package com.dzzdsj.design.pattern.demo.creational.AbstractFactoryPattern.ConcreteProduct;

import com.dzzdsj.design.pattern.demo.creational.AbstractFactoryPattern.AbstractProduct.Color;

public class Blue implements Color {
    @Override
    public void fill() {
        System.out.println("I'm Blue");
    }
}
