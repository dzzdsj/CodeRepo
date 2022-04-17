package com.dzzdsj.design.pattern.demo.structural.FacadePattern.Subsystem;

public class Square implements Shape {

    @Override
    public void draw() {
        System.out.println("Square::draw()");
    }
}
