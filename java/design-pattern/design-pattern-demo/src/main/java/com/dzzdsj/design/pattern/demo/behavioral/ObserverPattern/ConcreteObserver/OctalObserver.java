package com.dzzdsj.design.pattern.demo.behavioral.ObserverPattern.ConcreteObserver;

import com.dzzdsj.design.pattern.demo.behavioral.ObserverPattern.Observer.Observer;

public class OctalObserver extends Observer {

    @Override
    public void update() {
        System.out.println("Octal:" + Integer.toOctalString(subject.getState()));
    }
}
