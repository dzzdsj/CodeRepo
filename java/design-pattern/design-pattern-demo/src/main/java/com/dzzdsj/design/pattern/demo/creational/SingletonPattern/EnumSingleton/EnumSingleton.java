package com.dzzdsj.design.pattern.demo.creational.SingletonPattern.EnumSingleton;

import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.ObjectInputStream;
import java.io.ObjectOutputStream;

/**
 *  本目录中提到的其他几种实现单例的方式都有共同的缺点：
 * 1）需要额外的工作来实现序列化，否则每次反序列化一个序列化的对象时都会创建一个新的实例。
 * 2）可以使用反射强行调用私有构造器（如果要避免这种情况，可以修改构造器，让它在创建第二个实例的时候抛异常）。
 *而枚举类很好的解决了这两个问题，使用枚举除了线程安全和防止反射调用构造器之外，还提供了自动序列化机制，
 * 防止反序列化的时候创建新的对象。
 *
 */
public enum  EnumSingleton {
    INSTANCE;

    public static EnumSingleton getInstance() {
        return INSTANCE;
    }

    public static void main(String[] args) throws Exception{
        EnumSingleton enumSingleton1 = EnumSingleton.getInstance();
        EnumSingleton enumSingleton2 = EnumSingleton.getInstance();
        System.out.println(enumSingleton1 == enumSingleton2);//true

        // serialization
        FileOutputStream fos = new FileOutputStream("D:/tmp/TransientTest.txt");
        ObjectOutputStream oos = new ObjectOutputStream(fos);
        oos.writeObject(enumSingleton1);

        // de-serialization
        FileInputStream fis = new FileInputStream("D:/tmp/TransientTest.txt");
        ObjectInputStream ois = new ObjectInputStream(fis);
        EnumSingleton enumSingleton3 = (EnumSingleton)ois.readObject();
        System.out.println(enumSingleton1 == enumSingleton3);//true
    }
}
