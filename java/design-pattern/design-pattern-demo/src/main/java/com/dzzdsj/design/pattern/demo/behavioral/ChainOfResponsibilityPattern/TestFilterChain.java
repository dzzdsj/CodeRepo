package com.dzzdsj.design.pattern.demo.behavioral.ChainOfResponsibilityPattern;

import com.dzzdsj.design.pattern.demo.behavioral.ChainOfResponsibilityPattern.ConcreteHander.HTMLFilter;
import com.dzzdsj.design.pattern.demo.behavioral.ChainOfResponsibilityPattern.ConcreteHander.SensitiveFilter;

/**
 * 责任链设计模式技巧是定义一个过滤器接口，在接口中定义doFilter方法。由若干实现该接口的具体实现类来构成过滤器链
 */
public class TestFilterChain {
    public static void main(String[] args) {
        String s = "dkjg<skjfsk>ksjfl敏感slj十几个反动顺利开工建设了反动零售价格<jjk>";
        Request request = new Request();
        request.setRequest(s);
        System.out.println("begin:" + request);
        Response response = new Response();
        FilterChain filterChain = new FilterChain();
        filterChain.addFilter(new HTMLFilter())
                .addFilter(new SensitiveFilter());
        filterChain.doFilter(request, response);
        System.out.println("end:" + request);
    }
}
