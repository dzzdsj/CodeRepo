package com.dzzdsj.design.pattern.demo.structural.DecoratorPattern.Decorator;

import com.dzzdsj.design.pattern.demo.structural.DecoratorPattern.Component.Shape;

//步骤 3
//创建实现了 Shape 接口的抽象装饰类。
public abstract class ShapeDecorator implements Shape {
    protected Shape decoratedShape;//不使用继承，而将它做为一个属性
//构造函数接受Shape及其子类，引入了多态，这个子类可以重写父类方法来引入新的特性
    public ShapeDecorator(Shape decoratedShape) {
        this.decoratedShape = decoratedShape;
    }
//重写父类的方法
    @Override
    public void draw() {
        decoratedShape.draw();
    }
}
