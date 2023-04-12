package com.dzzdsj.design.pattern.demo.behavioral.VisitorPattern.ConcreteElement;

import com.dzzdsj.design.pattern.demo.behavioral.VisitorPattern.Element.ComputerPart;
import com.dzzdsj.design.pattern.demo.behavioral.VisitorPattern.Visitor.ComputerPartVisitor;

public class Monitor  implements ComputerPart {

    @Override
    public void accept(ComputerPartVisitor computerPartVisitor) {
        computerPartVisitor.visit(this);
    }
}
