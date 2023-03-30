package com.dzzdsj.j2se.serialize;

import java.io.*;

/**
 *transient is a variables modifier used in serialization. At the time of serialization, if we don’t want to save value of a particular variable in a file, then we use transient keyword.
 * <br>When JVM comes across transient keyword, it ignores original value of the variable and save default value of that variable data type.
 *
 * transient keyword plays an important role to meet security constraints. There are various real-life examples where we don’t want to save private data in file. Another use of transient keyword is not to serialize the variable whose value can be calculated/derived using other serialized objects or system such as age of a person, current date, etc.
 * Practically we serialized only those fields which represent a state of instance, after all serialization is all about to save state of an object to a file. It is good habit to use transient keyword with private confidential fields of a class during serialization.
 *
 *
 * transient and static : Since static fields are not part of state of the object, there is no use/impact of using transient keyword with static variables. However there is no compilation error.
 *
 * transient and final : final variables are directly serialized by their values, so there is no use/impact of declaring final variable as transient. There is no compile-time error though.
 *
 * 使用transient修饰的变量，在序列化/反序列化后，会使用变量的默认值替代原值
 * 当transient和static或final关键字一起使用时，transient无效
 */
public class TransientTest implements Serializable {
    // Normal variables
    int i = 10, j = 20;

    // Transient variables
    transient int k = 30;

    // Use of transient has no impact here
    transient static int l = 40;
    // Use of transient has no impact here
    transient final int m = 50;

    public static void main(String[] args) throws Exception
    {
        TransientTest input = new TransientTest();

        // serialization
        FileOutputStream fos = new FileOutputStream("D:/tmp/TransientTest.txt");
        ObjectOutputStream oos = new ObjectOutputStream(fos);
        oos.writeObject(input);

        // de-serialization
        FileInputStream fis = new FileInputStream("D:/tmp/TransientTest.txt");
        ObjectInputStream ois = new ObjectInputStream(fis);
        TransientTest output = (TransientTest)ois.readObject();
        System.out.println("i = " + output.i);
        System.out.println("j = " + output.j);
        System.out.println("k = " + output.k);
        System.out.println("l = " + output.l);
        System.out.println("m = " + output.m);
    }
}
/*
i= 10
j = 20
k = 0
l = 40
m = 50
*/
