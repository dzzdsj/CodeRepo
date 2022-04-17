package com.dzzdsj.design.pattern.demo.creational.FactoryMethodPattern.ConcreteCreator;

import com.dzzdsj.design.pattern.demo.creational.FactoryMethodPattern.ConcreteProduct.ConcreteProductB;
import com.dzzdsj.design.pattern.demo.creational.FactoryMethodPattern.Creator.IFactory;
import com.dzzdsj.design.pattern.demo.creational.FactoryMethodPattern.Product.IProduct;

public class ConcreteFactoryB implements IFactory {
    @Override
    public IProduct createProduct() {
        return new ConcreteProductB();
    }
}
