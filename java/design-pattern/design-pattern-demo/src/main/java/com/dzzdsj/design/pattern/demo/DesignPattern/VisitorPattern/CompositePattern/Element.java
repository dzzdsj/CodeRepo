package com.dzzdsj.design.pattern.demo.DesignPattern.VisitorPattern.CompositePattern;

/**
 * 接收访问者的类
 */
public interface Element {
    void accept(Visitor visitor);
}
