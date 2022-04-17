package com.dzzdsj.design.pattern.demo.structural.DecoratorPattern.ConcreteComponent;

import com.dzzdsj.design.pattern.demo.structural.DecoratorPattern.Component.Shape;

public class Circle implements Shape {

    @Override
    public void draw() {
        System.out.println("Shape: Circle");
    }
}
