package com.dzzdsj.design.pattern.demo.behavioral.MediatorPattern;

import com.dzzdsj.design.pattern.demo.behavioral.MediatorPattern.Mediatee.User;

/**
 * 中介者模式（Mediator Pattern）是用来降低多个对象和类之间的通信复杂性。
 * 简化交互-网状变星型
 * 用一个中介对象来封装一系列的对象交互，中介者使各对象不需要显式地相互引用，
 * 从而使其耦合松散，而且可以独立地改变它们之间的交互。将各对象之间的网状结构分
 * 离为星型结构。
 */
public class MediatorPatternDemo {
    public static void main(String[] args) {
        User robert = new User("Robert");
        User john = new User("John");

        robert.showMessage("hello");
        john.showMessage("hello2");
    }
}
