package com.dzzdsj.design.pattern.demo.creational.SingletonPattern.LazyStaticInnerClassSingleton;

import java.lang.reflect.Constructor;
import java.lang.reflect.InvocationTargetException;

/**
 * 利用静态内部类实现的懒汉式单例
 *
 * 是否 Lazy 初始化：是
 * 是否多线程安全：是
 * 实现难度：一般
 * 描述：这种方式能达到双检锁方式一样的功效，但实现更简单。对静态域使用延迟初始化，应使用这种方式而不是双检锁方式。这种方式只适用于静态域的情况，双检锁方式可在实例域需要延迟初始化时使用。
 * 这种方式同样利用了 classloader 机制来保证初始化 instance 时只有一个线程， Singleton 类被装载了，instance 不一定被初始化。因为 SingletonHolder 类没有被主动使用，
 * 只有通过显式调用 getInstance 方法时，才会显式装载 SingletonHolder 类，从而实例化 instance。
 */
public class LazyStaticInnerClassSingleton {
    /**
     * 规避了利用反射多次构建对象
     */
    private LazyStaticInnerClassSingleton(){
        if (LazyHolder.instance != null) {
            throw new RuntimeException("不允许创建多个实例");
        }
    }

    /**
     * 单纯的加private的话仍然能通过反射创建多个实例，参见以下main函数验证
     */
//    private LazyStaticInnerClassSingleton(){
//
//    }

    private static LazyStaticInnerClassSingleton getInstance() {
        return LazyHolder.instance;
    }

    private static class LazyHolder{
        private static final LazyStaticInnerClassSingleton instance = new LazyStaticInnerClassSingleton();
    }


    public static void main(String[] args) {
        Class<?> clazz = LazyStaticInnerClassSingleton.class;
        try {
            Constructor constructor = clazz.getDeclaredConstructor(null);
            constructor.setAccessible(true);
            Object object1 = constructor.newInstance();
            Object object2 = constructor.newInstance();
            System.out.println(object1 == object2);
        } catch (NoSuchMethodException e) {
            e.printStackTrace();
        } catch (IllegalAccessException e) {
            e.printStackTrace();
        } catch (InstantiationException e) {
            e.printStackTrace();
        } catch (InvocationTargetException e) {
            e.printStackTrace();
        }
    }
}
