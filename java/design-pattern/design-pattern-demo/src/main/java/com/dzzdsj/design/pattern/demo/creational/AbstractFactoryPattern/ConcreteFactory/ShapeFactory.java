package com.dzzdsj.design.pattern.demo.creational.AbstractFactoryPattern.ConcreteFactory;

import com.dzzdsj.design.pattern.demo.creational.AbstractFactoryPattern.AbstractFactory.AbstractFactory;
import com.dzzdsj.design.pattern.demo.creational.AbstractFactoryPattern.AbstractProduct.Color;
import com.dzzdsj.design.pattern.demo.creational.AbstractFactoryPattern.AbstractProduct.Shape;
import com.dzzdsj.design.pattern.demo.creational.AbstractFactoryPattern.ConcreteProduct.Circle;
import com.dzzdsj.design.pattern.demo.creational.AbstractFactoryPattern.ConcreteProduct.Square;

/**
 * 步骤 6
 * 创建扩展了 AbstractFactory 的工厂类，基于给定的信息生成实体类的对象。
 */
public class ShapeFactory extends AbstractFactory {

    @Override
    public Shape getShape(String shapeType) {
        if (shapeType == null) {
            return null;
        }
        if (shapeType.equalsIgnoreCase("CIRCLE")) {
            return new Circle();
        } else if (shapeType.equalsIgnoreCase("SQUARE")) {
            return new Square();
        }
        return null;
    }

    @Override
    public Color getColor(String color) {
        return null;
    }
}
