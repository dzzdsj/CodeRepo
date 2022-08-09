package com.dzzdsj.design.pattern.demo.behavioral.StatePattern.Context;

import com.dzzdsj.design.pattern.demo.behavioral.StatePattern.State.State;

//Context类保存了状态
public class Context {
    private State state;

    public Context() {
        state = null;
    }

    public void setState(State state) {
        this.state = state;
    }

    public State getState() {
        return state;
    }
}
