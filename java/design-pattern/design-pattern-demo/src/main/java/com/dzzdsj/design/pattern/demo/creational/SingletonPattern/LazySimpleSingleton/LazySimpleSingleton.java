package com.dzzdsj.design.pattern.demo.creational.SingletonPattern.LazySimpleSingleton;

/**
 * 懒汉式单例，在被使用的时候才实例化
 */
public class LazySimpleSingleton {
    private LazySimpleSingleton(){}

    private static LazySimpleSingleton instance = null;

    /**
     * 多线程下使用需要加同步锁
     * 并发高时阻塞严重
     * @return
     */
    public synchronized static LazySimpleSingleton getInstance() {
        if (instance == null) {
            instance = new LazySimpleSingleton();
        }
        return instance;
    }
}
