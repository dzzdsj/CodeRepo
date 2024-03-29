package com.dzzdsj.design.pattern.demo.structural.FacadePattern;

import com.dzzdsj.design.pattern.demo.structural.FacadePattern.Facade.ShapeMaker;

/**
 * 外观模式（Facade Pattern）隐藏系统的复杂性，并向客户端提供了一个客户端可以访问系统的接口
 * 类似漏斗，由粗至细，隐藏粗的部分，暴露细的部分，越细对外耦合度越低
 * 这种模式涉及到一个单一的类，该类提供了客户端请求的简化方法和对现有系统类方法的委托调用
 */
public class FacadePatternDemo {
    public static void main(String[] args) {
        ShapeMaker shapeMaker = new ShapeMaker();

        shapeMaker.drawCircle();
        shapeMaker.drawRectangle();
        shapeMaker.drawSquare();
    }
}
