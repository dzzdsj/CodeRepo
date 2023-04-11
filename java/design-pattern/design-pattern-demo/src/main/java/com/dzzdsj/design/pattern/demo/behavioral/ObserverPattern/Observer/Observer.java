package com.dzzdsj.design.pattern.demo.behavioral.ObserverPattern.Observer;

import com.dzzdsj.design.pattern.demo.behavioral.ObserverPattern.Subject.Subject;

/**
 * 观察者：为那些在目标发生改变时需获得通知的对象定义一个更新接口。
 */
public abstract class Observer {
    protected Subject subject;

    public Subject getSubject() {
        return subject;
    }

    public void setSubject(Subject subject) {
        this.subject = subject;
    }

    //更新接口
    public abstract void update();
}
