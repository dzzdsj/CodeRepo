package com.dzzdsj.design.pattern.demo.creational.SingletonPattern.LazyStaticInnerClassSingleton;

import java.lang.reflect.Constructor;
import java.lang.reflect.InvocationTargetException;

/**
 * 利用静态内部类实现的懒汉式单例
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
