package com.dzzdsj.design.pattern.demo.behavioral.VisitorPattern;

import com.dzzdsj.design.pattern.demo.behavioral.VisitorPattern.ConcreteElement.Computer;
import com.dzzdsj.design.pattern.demo.behavioral.VisitorPattern.ConcreteElement.Keyboard;
import com.dzzdsj.design.pattern.demo.behavioral.VisitorPattern.ConcreteVisitor.ComputerPartDisplayVisitor;
import com.dzzdsj.design.pattern.demo.behavioral.VisitorPattern.Element.ComputerPart;

public class VisitorPatternDemo {
    public static void main(String[] args) {
        ComputerPart computer = new Computer();
        computer.accept(new ComputerPartDisplayVisitor());
        System.out.println("===========");
        ComputerPart keyboard = new Keyboard();
        keyboard.accept(new ComputerPartDisplayVisitor());
    }
}
