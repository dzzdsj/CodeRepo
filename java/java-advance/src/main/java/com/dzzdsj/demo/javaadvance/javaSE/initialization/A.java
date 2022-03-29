package com.dzzdsj.demo.javaadvance.javaSE.initialization;

/**
 * 父类静态代码块-->子类静态代码块-->父类普通代码块-->父类构造方法-->子类代码块-->子类构造方法；
 */
class A{
    static {
        System.out.println("父类静态代码块");
    }
    public A(){
        System.out.println("父类构造方法");
    }
    {
        System.out.println("父类初始化块");
    }
}
 class B extends A{
    static{
        System.out.println("子类静态代码块");
    }
    public B(){
        System.out.println("子类构造方法");
    }
    {
        System.out.println("子类初始化块");
    }
    public static void main(String[] args){
        new B();
    }
}
