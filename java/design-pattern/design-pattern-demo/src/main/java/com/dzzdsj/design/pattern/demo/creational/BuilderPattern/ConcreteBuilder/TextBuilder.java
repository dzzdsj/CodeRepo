package com.dzzdsj.design.pattern.demo.creational.BuilderPattern.ConcreteBuilder;

import com.dzzdsj.design.pattern.demo.creational.BuilderPattern.Builder.Builder;

/**
 * 实现Builder接口
 * 构建具体的部件
 * 提供一个检索产品的接口
 */
public class TextBuilder extends Builder {
    @Override
    public void makeTitle(String title) {

    }

    @Override
    public void makeString(String string) {

    }

    @Override
    public void makeItems(String[] items) {

    }

    @Override
    public void close() {

    }

    /**
     * 提供一个检索产品的接口
     * @return
     */
    public String getResult() {
        return "";
    }
}
