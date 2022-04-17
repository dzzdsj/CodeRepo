package com.dzzdsj.design.pattern.demo.structural.FacadePattern.Subsystem;

public class Circle implements Shape {

    @Override
    public void draw() {
        System.out.println("Circle::draw()");
    }
}
