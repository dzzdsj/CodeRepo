package com.dzzdsj.demo.javaadvance.javaSE.This;


/**
 * 1.取对调用对象的引用。调用方法的对象是谁，this就是谁的引用。实际上编译器在处理方法调用时，就会传递一个调用者的引用，这里的this正好表示这个值。
 * 2.还经常用来处理成员变量和局部变量同名的情况
 * 3.使用this调用构造函数，必须在构造器最开始的位置，且只能使用1次
 */
public class ThisDemo {
    int i = 0;

    public ThisDemo(int i) {
        this.i = i;
    }

    /**
     * 可以利用这个进行链式编程，多次调用相同方法
     * @return
     */
    ThisDemo increament() {
        i++;
        return this;
    }

    void print() {
        System.out.println("i=" + i);
    }

    public static void main(String[] args) {
        ThisDemo thisDemo = new ThisDemo(100);
        thisDemo.increament().increament().print();//102
    }
}
