package com.dzzdsj.design.pattern.demo.DesignPatternRunoobDemo.BuilderPattern;

public class VegBurger extends Burger {
    @Override
    public String name() {
        return "VegBurger";
    }

    @Override
    public double price() {
        return 20.02d;
    }
}
