package com.dzzdsj.design.pattern.demo.DesignPatternRunoobDemo.BuilderPattern;

public class MealBurger extends Burger {
    @Override
    public String name() {
        return "MealBurger";
    }

    @Override
    public double price() {
        return 20.02d;
    }
}
