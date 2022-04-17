package com.dzzdsj.design.pattern.demo.creational.FactoryMethodPattern.Creator;

import com.dzzdsj.design.pattern.demo.creational.FactoryMethodPattern.Product.IProduct;

/**
 * 声明工厂方法，返回一个Product的实例。
 * 也可以定义一个工厂方法的默认实现。
 */
public interface IFactory {
    /**
     * factory method
     * @return
     */
    IProduct createProduct();
}
