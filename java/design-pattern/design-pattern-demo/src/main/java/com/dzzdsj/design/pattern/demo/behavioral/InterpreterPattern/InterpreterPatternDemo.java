package com.dzzdsj.design.pattern.demo.behavioral.InterpreterPattern;

import com.dzzdsj.design.pattern.demo.behavioral.InterpreterPattern.AbstractExpression.Expression;
import com.dzzdsj.design.pattern.demo.behavioral.InterpreterPattern.ConcreteExpression.AndExpression;
import com.dzzdsj.design.pattern.demo.behavioral.InterpreterPattern.ConcreteExpression.OrExpression;
import com.dzzdsj.design.pattern.demo.behavioral.InterpreterPattern.ConcreteExpression.TerminalExpression;

public class InterpreterPatternDemo {
    public static Expression getMaleExpression() {
        Expression robert = new TerminalExpression("Robert");
        Expression john = new TerminalExpression("John");
        return new OrExpression(robert, john);
    }

    public static Expression getMarriedWomanExpression(){
        Expression julie = new TerminalExpression("Julie");
        Expression married = new TerminalExpression("Married");
        return new AndExpression(julie, married);
    }
    public static void main(String[] args) {
         Expression isMale = getMaleExpression();
        Expression isMarriedWoman = getMarriedWomanExpression();
        System.out.println("John or Robert is male? " + isMale.interpret("John"));
        System.out.println("Julie is a married women? "
                + isMarriedWoman.interpret("Married Julie"));
    }
}
