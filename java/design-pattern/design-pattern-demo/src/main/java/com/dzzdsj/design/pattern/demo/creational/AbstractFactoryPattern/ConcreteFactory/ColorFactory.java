package com.dzzdsj.design.pattern.demo.creational.AbstractFactoryPattern.ConcreteFactory;

import com.dzzdsj.design.pattern.demo.creational.AbstractFactoryPattern.AbstractFactory.AbstractFactory;
import com.dzzdsj.design.pattern.demo.creational.AbstractFactoryPattern.AbstractProduct.Color;
import com.dzzdsj.design.pattern.demo.creational.AbstractFactoryPattern.AbstractProduct.Shape;
import com.dzzdsj.design.pattern.demo.creational.AbstractFactoryPattern.ConcreteProduct.Blue;
import com.dzzdsj.design.pattern.demo.creational.AbstractFactoryPattern.ConcreteProduct.Green;

/**
 * 步骤 6
 * 创建扩展了 AbstractFactory 的工厂类，基于给定的信息生成实体类的对象。
 */
public class ColorFactory extends AbstractFactory {
    @Override
    public Shape getShape(String shapeType) {
        return null;
    }

    @Override
    public Color getColor(String color) {
        if (color == null) {
            return null;
        }
        if (color.equalsIgnoreCase("GREEN")) {
            return new Green();
        } else if (color.equalsIgnoreCase("BLUE")) {
            return new Blue();
        }
        return null;
    }
}
