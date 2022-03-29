package com.dzzdsj.design.pattern.demo.DesignPattern.VisitorPattern.CompositePattern;

public class ListVisitor extends Visitor {
    //当前正在访问的目录
    private String currentDir = "";

    @Override
    void visit(File file) {
        System.out.println(currentDir + "/" + file);
    }

    @Override
    void visit(Directory directory) {
        System.out.println(currentDir + "/" + directory);
        String saveDir = currentDir;
        currentDir = currentDir + "/" + directory.getName();
        // TODO: 2020/6/19
//        Iterator iterator = 
    }
}
