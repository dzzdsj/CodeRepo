package com.dzzdsj.design.pattern.demo.DesignPattern.PrototypePattern;

public interface Product extends Cloneable {
    void use(String s);

    Product createClone();
}
