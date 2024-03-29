package com.dzzdsj.design.pattern.demo.creational.SingletonPattern.HungrySingleton;

/**
 * 饿汉式
 * 是否 Lazy 初始化：否
 * 是否多线程安全：是
 * 实现难度：易
 * 描述：这种方式比较常用，但容易产生垃圾对象。
 * 优点：没有加锁，执行效率会提高。
 * 缺点：类加载时就初始化，浪费内存。适用于单例对象较少的情况
 * 它基于 classloader 机制避免了多线程的同步问题，不过，instance 在类装载时就实例化，
 * 虽然导致类装载的原因有很多种，在单例模式中大多数都是调用 getInstance 方法，
 * 但是也不能确定有其他的方式（或者其他的静态方法）导致类装载，这时候初始化 instance 显然没有达到
 * lazy loading 的效果。
 *
 * 注意：序列化反序列化后得到的对象和原来内存中的对象是不同的，不太适用于单例对象。
 *
 */
public class SingleObject {
    //要点1：在类加载时就 创建 SingleObject 的一个对象
    //static修饰，在类加载时初始化
    private static SingleObject instance = new SingleObject();

    //要点2：让构造函数为 private，这样该类就不会被实例化（使用构造函数方式）
    private SingleObject() {
    }

    //要点3：另外提供一个获取实例的方法，获取唯一可用的对象
    //由于无法通过构造函数实例化对象了，所以获取实例的方法需要是static的
    public static SingleObject getInstance() {
        return instance;
    }

    public void showMessage() {
        System.out.println("Hello World!");
    }
}
