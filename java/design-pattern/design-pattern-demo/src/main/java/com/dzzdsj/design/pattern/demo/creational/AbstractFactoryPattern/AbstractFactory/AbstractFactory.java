package com.dzzdsj.design.pattern.demo.creational.AbstractFactoryPattern.AbstractFactory;

import com.dzzdsj.design.pattern.demo.creational.AbstractFactoryPattern.AbstractProduct.Color;
import com.dzzdsj.design.pattern.demo.creational.AbstractFactoryPattern.AbstractProduct.Shape;

/**
 * 声明生成抽象产品的操作接口。
 */
public abstract class   AbstractFactory {
    public abstract Color getColor(String color);

    public abstract Shape getShape(String shape);
}
