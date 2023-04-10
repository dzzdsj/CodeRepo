package com.dzzdsj.design.pattern.demo.behavioral.CommandPattern.Receiver;

//步骤 2
//创建一个请求类。
public class Stock {

    private String name = "ABC";
    private int quantity = 10;
//两种不同的操作buy、sell
    public void buy() {
        System.out.println("Stock [ Name: " + name + ",Quantity: " + quantity + " ] bought");
    }

    public void sell() {
        System.out.println("Stock [ Name: " + name + ",Quantity: " + quantity + " ] sold");
    }
}
