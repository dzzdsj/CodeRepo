package com.dzzdsj.design.pattern.demo.behavioral.ChainOfResponsibilityPattern;

import com.dzzdsj.design.pattern.demo.behavioral.ChainOfResponsibilityPattern.Hander.Filter;

import java.util.ArrayList;
import java.util.List;

public class FilterChain {
    List<Filter> filterList = new ArrayList<>();

    public FilterChain addFilter(Filter filter) {
        this.filterList.add(filter);
        return this;
    }

    public String doFilter(Request request, Response response) {
        for(Filter filter: filterList){
            filter.doFilter(request, response);
        }
        return request.getRequest();
    }
}
