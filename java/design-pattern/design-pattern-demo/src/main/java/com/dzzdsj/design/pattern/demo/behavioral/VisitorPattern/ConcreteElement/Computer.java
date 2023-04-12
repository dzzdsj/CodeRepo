package com.dzzdsj.design.pattern.demo.behavioral.VisitorPattern.ConcreteElement;

import com.dzzdsj.design.pattern.demo.behavioral.VisitorPattern.Element.ComputerPart;
import com.dzzdsj.design.pattern.demo.behavioral.VisitorPattern.Visitor.ComputerPartVisitor;

public class Computer implements ComputerPart {

    ComputerPart[] parts;

    public Computer(){
        parts = new ComputerPart[] {new Mouse(), new Keyboard(), new Monitor()};
    }


    @Override
    public void accept(ComputerPartVisitor computerPartVisitor) {
        for (int i = 0; i < parts.length; i++) {
            parts[i].accept(computerPartVisitor);
        }
        computerPartVisitor.visit(this);
    }
}
