package com.dzzdsj.design.pattern.demo.behavioral.InterpreterPattern.ConcreteExpression;

import com.dzzdsj.design.pattern.demo.behavioral.InterpreterPattern.AbstractExpression.Expression;

public class TerminalExpression implements Expression {
    private String data;

    public TerminalExpression(String data) {
        this.data = data;
    }

    @Override
    public boolean interpret(String context) {
        if (context.contains(data)) {
            return true;
        }
        return false;
    }
}
