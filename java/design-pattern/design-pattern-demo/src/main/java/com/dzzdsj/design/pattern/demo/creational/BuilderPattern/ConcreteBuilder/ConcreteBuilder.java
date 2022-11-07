package com.dzzdsj.design.pattern.demo.creational.BuilderPattern.ConcreteBuilder;

import com.dzzdsj.design.pattern.demo.creational.BuilderPattern.Builder.Builder;

public class ConcreteBuilder extends Builder {
    private String context = "";

    @Override
    public Builder buildPartA() {
        StringBuilder stringBuilder = new StringBuilder(context);
        stringBuilder.append("buildPartA");
        this.context = new String(stringBuilder);
        return this;
    }

    @Override
    public Builder buildPartB() {
        StringBuilder stringBuilder = new StringBuilder(context);
        stringBuilder.append("buildPartB");
        this.context = new String(stringBuilder);
        return this;
    }

    public void getResult() {
        System.out.println("context=" + context);
    }
}
