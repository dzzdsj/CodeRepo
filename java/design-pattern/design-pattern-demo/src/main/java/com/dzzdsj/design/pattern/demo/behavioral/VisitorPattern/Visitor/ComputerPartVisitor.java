package com.dzzdsj.design.pattern.demo.behavioral.VisitorPattern.Visitor;

import com.dzzdsj.design.pattern.demo.behavioral.VisitorPattern.ConcreteElement.Computer;
import com.dzzdsj.design.pattern.demo.behavioral.VisitorPattern.ConcreteElement.Keyboard;
import com.dzzdsj.design.pattern.demo.behavioral.VisitorPattern.ConcreteElement.Monitor;
import com.dzzdsj.design.pattern.demo.behavioral.VisitorPattern.ConcreteElement.Mouse;

/**
 * Visitor： 为ConcreteElement的每一个类声明一个visit操作
 */
public interface ComputerPartVisitor {
    void visit(Computer computer);

    void visit(Mouse mouse);

    void visit(Keyboard keyboard);

    void visit(Monitor monitor);
}
