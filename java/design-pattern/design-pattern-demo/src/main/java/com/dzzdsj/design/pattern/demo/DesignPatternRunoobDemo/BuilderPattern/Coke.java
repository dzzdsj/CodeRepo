package com.dzzdsj.design.pattern.demo.DesignPatternRunoobDemo.BuilderPattern;

public class Coke extends ColdDrink {

    @Override
    public String name() {
        return "Coke";
    }

    @Override
    public double price() {
        return 1.2d;
    }
}
