package com.dzzdsj.design.pattern.demo.behavioral.CommandPattern.Invoker;

import com.dzzdsj.design.pattern.demo.behavioral.CommandPattern.Command.Order;

import java.util.ArrayList;
import java.util.List;

//步骤 4
//创建命令调用类。
public class Broker {
    private List<Order> orderList = new ArrayList<Order>();
//添加命令
    public void takeOrder(Order order) {
        orderList.add(order);
    }
    //执行所有命令
    public void placeOrders() {
        for (Order order : orderList) {
            order.execute();
        }
        orderList.clear();
    }
}
