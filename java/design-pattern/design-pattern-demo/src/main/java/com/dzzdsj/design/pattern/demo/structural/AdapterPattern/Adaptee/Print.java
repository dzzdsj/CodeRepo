package com.dzzdsj.design.pattern.demo.structural.AdapterPattern.Adaptee;

/**
 * 扮演需要适配器实现的接口，即增加的新的能力
 */
public interface Print {
    void printWeak();

    void printStrong();
}
