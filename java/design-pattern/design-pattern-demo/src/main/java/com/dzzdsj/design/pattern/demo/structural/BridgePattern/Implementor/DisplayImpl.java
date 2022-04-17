package com.dzzdsj.design.pattern.demo.structural.BridgePattern.Implementor;

/**
 * 类的实现层次结构的最上层
 */
public abstract class DisplayImpl {
    /**
     * 实现层次结构中方法的最原始的定义
     */
    public abstract void rawOpen();

    public abstract void rawPrint();

    public abstract void rawClose();
}
