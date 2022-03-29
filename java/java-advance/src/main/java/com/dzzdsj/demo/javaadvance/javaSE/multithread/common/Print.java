package com.dzzdsj.demo.javaadvance.javaSE.multithread.common;

public  class Print {
    public static void printThreadName() {
        System.out.printf("Welcome! I'm %s.%n", Thread.currentThread().getName());
    }
}
