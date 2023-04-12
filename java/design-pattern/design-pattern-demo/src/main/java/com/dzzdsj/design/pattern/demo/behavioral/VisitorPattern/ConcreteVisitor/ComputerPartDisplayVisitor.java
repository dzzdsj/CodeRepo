package com.dzzdsj.design.pattern.demo.behavioral.VisitorPattern.ConcreteVisitor;

import com.dzzdsj.design.pattern.demo.behavioral.VisitorPattern.ConcreteElement.Computer;
import com.dzzdsj.design.pattern.demo.behavioral.VisitorPattern.ConcreteElement.Keyboard;
import com.dzzdsj.design.pattern.demo.behavioral.VisitorPattern.ConcreteElement.Monitor;
import com.dzzdsj.design.pattern.demo.behavioral.VisitorPattern.ConcreteElement.Mouse;
import com.dzzdsj.design.pattern.demo.behavioral.VisitorPattern.Visitor.ComputerPartVisitor;

public class ComputerPartDisplayVisitor implements ComputerPartVisitor {

    @Override
    public void visit(Computer computer) {
        System.out.println("Displaying Computer.");
    }

    @Override
    public void visit(Mouse mouse) {
        System.out.println("Displaying Mouse.");
    }

    @Override
    public void visit(Keyboard keyboard) {
        System.out.println("Displaying Keyboard.");
    }

    @Override
    public void visit(Monitor monitor) {
        System.out.println("Displaying Monitor.");
    }
}
