package com.dzzdsj.design.pattern.demo.behavioral.StatePattern.State;

import com.dzzdsj.design.pattern.demo.behavioral.StatePattern.Context.Context;

//状态接口
public interface State {
    void doAction(Context context);
}
