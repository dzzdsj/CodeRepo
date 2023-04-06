package com.dzzdsj.design.pattern.demo.creational.SingletonPattern.LazyDoubleCheckSingleton;

/**
 * 双重检测懒汉式单例
 * 是否 Lazy 初始化：是
 *
 * 是否多线程安全：是
 *
 * 实现难度：较复杂
 *
 * 描述：这种方式采用双锁机制，安全且在多线程情况下能保持高性能。
 * getInstance() 的性能对应用程序很关键。
 */
public class LazyDoubleCheckSingleton {
    private volatile static LazyDoubleCheckSingleton instance;

    private LazyDoubleCheckSingleton() {
    }

    /**
     * 第三版
     */
    public static LazyDoubleCheckSingleton getInstance() {
        /**
         * 进一步改进版，只针new的过程加锁,且对判断null的过程加同步
         */
        //大部分情况下，不会进入加锁的代码块，同时保证第一次获取实例时是线程安全
        if (instance == null) {
            synchronized (LazyDoubleCheckSingleton.class) {
                //双重判断
                if(instance == null) {
                    instance = new LazyDoubleCheckSingleton();
                }
            }
        }
        //do something
        return instance;
    }

    /**
     * 第二版
     */

//    public static LazyDoubleCheckSingleton getInstance() {
//        /**
//         * 进一步改进版，只针new的过程加锁,但是变成了线程不安全了。两个线程可能同时判断为null
//         */
//
//        if (instance == null) {
//            synchronized (LazyDoubleCheckSingleton.class) {
//                instance = new LazyDoubleCheckSingleton();
//            }
//        }
//        //do something
//        return instance;
//    }
    /**
     * 第一版
     */
//    public static LazyDoubleCheckSingleton getInstance() {
//        /**
//         * 改进版，缩小加锁的代码块，只针对实例化的过程加锁
//         */
//        synchronized (LazyDoubleCheckSingleton.class) {
//            if (instance == null) {
//                instance = new LazyDoubleCheckSingleton();
//            }
//        }
//        //do something
//        return instance;
//    }
}
