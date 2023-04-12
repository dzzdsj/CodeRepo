package com.dzzdsj.design.pattern.demo.behavioral.TemplateMethodPattern.ConcreteClass;

import com.dzzdsj.design.pattern.demo.behavioral.TemplateMethodPattern.AbstractClass.AbstractDisplay;

/**
 * 父类抽象类的具体实现
 */
public class CharDisplay extends AbstractDisplay {
    private char ch;

    public CharDisplay(char ch) {
        this.ch = ch;
    }

    @Override
    public void open() {
        System.out.print("<");
    }

    @Override
    protected void close() {
        System.out.println(">");
    }

    @Override
    protected void print() {
        System.out.print(ch);
    }
}
