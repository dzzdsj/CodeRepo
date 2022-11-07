package com.dzzdsj.design.pattern.demo.creational.AbstractFactoryPattern.AbstractFactory;

import com.dzzdsj.design.pattern.demo.creational.AbstractFactoryPattern.AbstractProduct.AbstractProductA;
import com.dzzdsj.design.pattern.demo.creational.AbstractFactoryPattern.AbstractProduct.AbstractProductB;

/**
 * 创建抽象产品对象的操作接口。
 */
public abstract class AbstractFactory {
    public abstract AbstractProductA createProductA(String product);

    public abstract AbstractProductB createProductB(String product);
}
