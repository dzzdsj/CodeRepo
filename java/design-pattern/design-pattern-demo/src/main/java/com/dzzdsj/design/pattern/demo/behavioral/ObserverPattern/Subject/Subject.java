package com.dzzdsj.design.pattern.demo.behavioral.ObserverPattern.Subject;

import com.dzzdsj.design.pattern.demo.behavioral.ObserverPattern.Observer.Observer;

import java.util.ArrayList;
import java.util.List;

/**
 * 目标对象。它知道它的观察者，可以有任意多个观察者观察同一目标。
 * 提供注册和删除观察者的接口
 */
public class Subject {
    //允许任意多个观察者同时注册
    private List<Observer> observerList = new ArrayList<>();

    //表示所观察对象的状态
    private int state;

    public int getState() {
        return state;
    }

    public void setState(int state) {
        this.state = state;
        //状态变更了，就通知观察者
        notifyAllObserver();
    }

    //注册观察者
    public void attach(Observer observer) {
        observer.setSubject(this);
        observerList.add(observer);
    }

    //删除观察者
    public void detach(Observer observer) {
        observerList.remove(observer);
    }
    //通知观察者更新
    public void notifyAllObserver() {
        for (Observer observer : observerList) {
            observer.update();
        }
    }
}
