package com.dzzdsj.design.pattern.demo.behavioral.CommandPattern.ConcreteCommand;

import com.dzzdsj.design.pattern.demo.behavioral.CommandPattern.Command.Order;
import com.dzzdsj.design.pattern.demo.behavioral.CommandPattern.Receiver.Stock;

public class SellStock implements Order {
    private Stock abcStock;

    public SellStock(Stock abcStock) {
        this.abcStock = abcStock;
    }

    public void execute() {
        abcStock.sell();
    }
}
