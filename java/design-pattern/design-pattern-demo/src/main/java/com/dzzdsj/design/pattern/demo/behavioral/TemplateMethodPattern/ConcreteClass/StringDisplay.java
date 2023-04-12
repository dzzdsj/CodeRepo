package com.dzzdsj.design.pattern.demo.behavioral.TemplateMethodPattern.ConcreteClass;

import com.dzzdsj.design.pattern.demo.behavioral.TemplateMethodPattern.AbstractClass.AbstractDisplay;

/**
 * 父类抽象类的具体实现
 */
public class StringDisplay extends AbstractDisplay {
    private String string;
    private int width;

    public StringDisplay(String string) {
        this.string = string;
        this.width = string.getBytes().length;
    }

    @Override
    public void open() {
        printLine();
    }

    @Override
    protected void close() {
        printLine();
    }

    @Override
    protected void print() {
        System.out.println("|" + string + "|");
    }

    private void printLine() {
        System.out.print("+");
        for (int i = 0; i < width; i++) {
            System.out.print("-");
        }
        System.out.println("+");
    }
}
