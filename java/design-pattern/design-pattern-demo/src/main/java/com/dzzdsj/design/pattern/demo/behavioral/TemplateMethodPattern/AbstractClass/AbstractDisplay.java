package com.dzzdsj.design.pattern.demo.behavioral.TemplateMethodPattern.AbstractClass;

/**
 * 抽象父类，只实现执行逻辑部分，其余的交给子类来实现
 */
public abstract class AbstractDisplay {
     protected abstract void open();

    protected abstract void close();

    protected abstract void print();

    /**
     * 实现逻辑：定义执行逻辑并声明为final，阻止子类重写
     */
    public final void display() {
        open();
        for (int i = 0; i < 5; i++) {
            print();
        }
        close();
    }
}
