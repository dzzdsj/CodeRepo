package com.dzzdsj.design.pattern.demo.behavioral.ChainOfResponsibilityPattern.ConcreteHander;

import com.dzzdsj.design.pattern.demo.behavioral.ChainOfResponsibilityPattern.Hander.Filter;
import com.dzzdsj.design.pattern.demo.behavioral.ChainOfResponsibilityPattern.Request;
import com.dzzdsj.design.pattern.demo.behavioral.ChainOfResponsibilityPattern.Response;

public class HTMLFilter implements Filter {
    @Override
    public void doFilter(Request request, Response response) {
        String s = request.getRequest().replace("<", "[")
                .replace(">", "]");
        request.setRequest(s);
    }
}
