package com.dzzdsj.design.pattern.demo.structural.FacadePattern.Subsystem;

public class Rectangle implements Shape {

    @Override
    public void draw() {
        System.out.println("Rectangle::draw()");
    }
}
