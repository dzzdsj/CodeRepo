package com.dzzdsj.design.pattern.demo.behavioral.ObserverPattern.ConcreteObserver;

import com.dzzdsj.design.pattern.demo.behavioral.ObserverPattern.Observer.Observer;

public class BinaryObserver extends Observer {

    @Override
    public void update() {
        System.out.println("Binary:" + Integer.toBinaryString(subject.getState()));
    }
}
