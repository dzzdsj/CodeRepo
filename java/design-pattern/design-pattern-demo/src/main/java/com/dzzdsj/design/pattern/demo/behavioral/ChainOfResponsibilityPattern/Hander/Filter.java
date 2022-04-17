package com.dzzdsj.design.pattern.demo.behavioral.ChainOfResponsibilityPattern.Hander;

import com.dzzdsj.design.pattern.demo.behavioral.ChainOfResponsibilityPattern.Request;
import com.dzzdsj.design.pattern.demo.behavioral.ChainOfResponsibilityPattern.Response;

public interface Filter {
    void doFilter(Request request, Response response);
}
