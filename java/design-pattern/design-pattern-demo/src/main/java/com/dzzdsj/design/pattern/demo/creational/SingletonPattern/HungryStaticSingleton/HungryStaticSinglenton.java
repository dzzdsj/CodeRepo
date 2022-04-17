package com.dzzdsj.design.pattern.demo.creational.SingletonPattern.HungryStaticSingleton;
/**
 * 饿汉式静态块单例模式
 */
public class HungryStaticSinglenton {
    private static final HungryStaticSinglenton hungryStaticSinglenton;

    /**
     * 使用静态块初始化
     */
    static {
        hungryStaticSinglenton = new HungryStaticSinglenton();
    }

    /**
     * 构造函数定义为private
     */
    private HungryStaticSinglenton(){};

    public static HungryStaticSinglenton getInstance() {
        return hungryStaticSinglenton;
    }
}
