package com.dzzdsj.demo.codeutils.DesignPatternRunoobDemo.FactoryPattern;

/**
 * 步骤 3
 * 创建一个工厂，生成基于给定信息的实体类的对象。
 */
public class ShapeFactory {
    //使用 getShape 方法获取形状类型的对象
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
}
