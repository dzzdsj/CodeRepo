package com.dzzdsj.design.pattern.demo.creational.SingletonPattern.LazyDoubleCheckSingleton;

/**
 * 双重检测懒汉式单例
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
//         * 改进版，只针对实例化的过程加锁,
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
