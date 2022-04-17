package com.dzzdsj.design.pattern.demo.structural.DecoratorPattern.ConcreteComponent;

import com.dzzdsj.design.pattern.demo.structural.DecoratorPattern.Component.Shape;

public class Rectangle implements Shape {

    @Override
    public void draw() {
        System.out.println("Shape: Rectangle");
    }
}
