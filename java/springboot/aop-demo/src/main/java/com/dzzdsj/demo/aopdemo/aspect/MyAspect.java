package com.dzzdsj.demo.aopdemo.aspect;

import com.dzzdsj.demo.aopdemo.annotation.AopAnnotation;
import org.aspectj.lang.ProceedingJoinPoint;
import org.aspectj.lang.annotation.Around;
import org.aspectj.lang.annotation.Aspect;
import org.aspectj.lang.annotation.Pointcut;
import org.springframework.stereotype.Component;

@Aspect
@Component
public class MyAspect {
    @Pointcut("@annotation(aopAnnotation)")
    public void myPointcut(AopAnnotation aopAnnotation) {
    }
    @Around("myPointcut(aopAnnotation)")
    public void myAdvice(ProceedingJoinPoint joinPoint,AopAnnotation aopAnnotation) {
        System.out.println(aopAnnotation.name()+"hello");
    }
}
