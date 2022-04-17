package com.dzzdsj.design.pattern.demo.structural.CompositePattern.Leaf;

import com.dzzdsj.design.pattern.demo.structural.CompositePattern.Component.Entry;

/**
 * 文件类
 */
public class File extends Entry {
    private String name;
    private int size;

    public File(String name, int size) {
        this.name = name;
        this.size = size;
    }

    @Override
    public String getName() {
        return name;
    }

    @Override
    public int getSize() {
        return size;
    }

    @Override
    public void printList(String prefix) {
        //字符串+this 自动调用tostring方法
        System.out.println(prefix + "/" + this);
    }
}
