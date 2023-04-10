package com.dzzdsj.design.pattern.demo.structural.FacadePattern.Facade;

import com.dzzdsj.design.pattern.demo.structural.FacadePattern.Subsystem.Circle;
import com.dzzdsj.design.pattern.demo.structural.FacadePattern.Subsystem.Rectangle;
import com.dzzdsj.design.pattern.demo.structural.FacadePattern.Subsystem.Shape;
import com.dzzdsj.design.pattern.demo.structural.FacadePattern.Subsystem.Square;

//步骤 3
//创建一个外观类。

/**
 * 定义一个高级接口，为系统中的一组接口提供一个一致的界面（通过ShapeMaker调用各个类的draw接口）
 */
public class ShapeMaker {
    private Shape circle;
    private Shape rectangle;
    private Shape square;

    public ShapeMaker() {
        circle = new Circle();
        rectangle = new Rectangle();
        square = new Square();
    }

    public void drawCircle() {
        circle.draw();
    }

    public void drawRectangle() {
        rectangle.draw();
    }

    public void drawSquare() {
        square.draw();
    }
}
