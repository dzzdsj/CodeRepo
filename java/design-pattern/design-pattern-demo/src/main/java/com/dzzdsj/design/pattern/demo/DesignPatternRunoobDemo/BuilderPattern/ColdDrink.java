package com.dzzdsj.design.pattern.demo.DesignPatternRunoobDemo.BuilderPattern;

public abstract class ColdDrink implements Item {

    @Override
    public Packing packing() {
        return new Bottle();
    }

    @Override
    public abstract double price();
}
