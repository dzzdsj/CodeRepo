package com.dzzdsj.demo.aopdemo;

import org.aopalliance.intercept.MethodInterceptor;
import org.aopalliance.intercept.MethodInvocation;


public class MyInterceptor implements MethodInterceptor {
    @Override
    public Object invoke(MethodInvocation methodInvocation) throws Throwable {
        System.out.println("======================================");
        System.out.println("enter invoke");
        System.out.println("======================================");
        return null;
    }
}
