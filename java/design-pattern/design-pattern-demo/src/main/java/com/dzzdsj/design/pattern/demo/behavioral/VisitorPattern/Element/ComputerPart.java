package com.dzzdsj.design.pattern.demo.behavioral.VisitorPattern.Element;

import com.dzzdsj.design.pattern.demo.behavioral.VisitorPattern.Visitor.ComputerPartVisitor;

public interface ComputerPart {
    //定义一个以访问者为参数的accept操作
    void accept(ComputerPartVisitor computerPartVisitor);
}
