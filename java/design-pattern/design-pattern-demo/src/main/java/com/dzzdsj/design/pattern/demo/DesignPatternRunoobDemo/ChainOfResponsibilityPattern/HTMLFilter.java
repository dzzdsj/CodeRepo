package com.dzzdsj.design.pattern.demo.DesignPatternRunoobDemo.ChainOfResponsibilityPattern;

public class HTMLFilter implements Filter {
    @Override
    public void doFilter(Request request, Response response) {
        String s = request.getRequest().replace("<", "[")
                .replace(">", "]");
        request.setRequest(s);
    }
}
