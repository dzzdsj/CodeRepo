package com.dzzdsj.design.pattern.demo.structural.CompositePattern.Component;

/**
 * 表示目录条目的抽象类:统一了 File 和 Directory 类
 */
public abstract class Entry {
    public abstract String getName();

    public abstract int getSize();

    public Entry add(Entry entry) throws FileTreatmentException {
        throw new FileTreatmentException();
    }

    //打印目录条目一览
    void printList() {
        printList("");
    }

    //打印带前缀的
    public abstract void printList(String prefix);

    @Override
    public String toString() {
        return getName() + "(" + getSize() + ")";
    }
}
