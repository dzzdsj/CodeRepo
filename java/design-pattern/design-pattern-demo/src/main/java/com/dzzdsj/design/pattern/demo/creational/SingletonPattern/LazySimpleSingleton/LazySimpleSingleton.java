package com.dzzdsj.design.pattern.demo.creational.SingletonPattern.LazySimpleSingleton;

/**
 * 懒汉式单例，在被使用的时候才实例化
 *
 * 是否 Lazy 初始化：是
 *
 * 是否多线程安全：是
 *
 * 实现难度：易
 *
 * 描述：这种方式具备很好的 lazy loading，能够在多线程中很好的工作，但是，效率很低，99% 情况下不需要同步。
 * 优点：第一次调用才初始化，避免内存浪费。
 * 缺点：必须加锁 synchronized 才能保证单例，但加锁会影响效率。
 * getInstance() 的性能对应用程序不是很关键（该方法使用不太频繁）。
 */
public class LazySimpleSingleton {
    private LazySimpleSingleton(){}
//相比普通的饿汉型，不在类加载时直接初始化了
    private static LazySimpleSingleton instance = null;

    /**
     * 多线程下使用需要加同步锁
     * 并发高时阻塞严重
     * @return
     */
    public static synchronized  LazySimpleSingleton getInstance() {
        //初始化时加入null值判断，为了线程安全，需要加同步
        if (instance == null) {
            instance = new LazySimpleSingleton();
        }
        return instance;
    }
}
