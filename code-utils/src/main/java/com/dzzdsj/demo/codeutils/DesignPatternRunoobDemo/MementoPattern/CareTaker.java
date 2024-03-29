package com.dzzdsj.demo.codeutils.DesignPatternRunoobDemo.MementoPattern;
//Caretaker 对象负责从 Memento 中恢复对象的状态

import java.util.ArrayList;
import java.util.List;

public class CareTaker {
    private List<Memento> mementoList = new ArrayList<Memento>();

    public void add(Memento state) {
        mementoList.add(state);
    }

    public Memento get(int index) {
        return mementoList.get(index);
    }
}
