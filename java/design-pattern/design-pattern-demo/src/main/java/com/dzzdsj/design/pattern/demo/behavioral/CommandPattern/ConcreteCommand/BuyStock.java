package com.dzzdsj.design.pattern.demo.behavioral.CommandPattern.ConcreteCommand;

import com.dzzdsj.design.pattern.demo.behavioral.CommandPattern.Command.Order;
import com.dzzdsj.design.pattern.demo.behavioral.CommandPattern.Receiver.Stock;

public class BuyStock implements Order {
    private Stock abcStock;

    public BuyStock(Stock abcStock) {
        this.abcStock = abcStock;
    }

    public void execute() {
        abcStock.buy();
    }
}
