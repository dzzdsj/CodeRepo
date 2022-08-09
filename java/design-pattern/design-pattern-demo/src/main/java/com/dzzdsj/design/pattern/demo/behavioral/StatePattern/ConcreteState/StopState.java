package com.dzzdsj.design.pattern.demo.behavioral.StatePattern.ConcreteState;

import com.dzzdsj.design.pattern.demo.behavioral.StatePattern.Context.Context;
import com.dzzdsj.design.pattern.demo.behavioral.StatePattern.State.State;

public class StopState implements State {

    public void doAction(Context context) {
        System.out.println("Player is in stop state");
        context.setState(this);//保存状态到context中
    }

    public String toString() {
        return "Stop State";
    }
}
