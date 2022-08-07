package com.dzzdsj.design.pattern.demo.behavioral.StrategyPattern.ConcreteStrategy;

import com.dzzdsj.design.pattern.demo.behavioral.StrategyPattern.Strategy.Strategy;

public class OperationMultiply implements Strategy {
    @Override
    public int doOperation(int num1, int num2) {
        return num1 * num2;
    }
}
