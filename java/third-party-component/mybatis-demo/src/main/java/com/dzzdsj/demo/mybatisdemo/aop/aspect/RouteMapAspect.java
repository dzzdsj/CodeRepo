package com.dzzdsj.demo.mybatisdemo.aop.aspect;

import com.dzzdsj.demo.mybatisdemo.annotation.routemap.RouteMapMapper;
import org.aspectj.lang.ProceedingJoinPoint;
import org.aspectj.lang.annotation.Around;
import org.aspectj.lang.annotation.Aspect;
import org.aspectj.lang.annotation.Pointcut;
import org.springframework.stereotype.Component;

@Component
@Aspect
public class RouteMapAspect {
    @Pointcut("@annotation(routeMapMapper)")
    public void pointcutRouteMapMapper(RouteMapMapper routeMapMapper) {
    }

    @Around("pointcutRouteMapMapper(routeMapMapper)")
    public Object routeMapMapperAdvice(ProceedingJoinPoint proceedingJoinPoint,RouteMapMapper routeMapMapper) throws Throwable {
        System.out.println("=====================routeMapMapperAdvice=========================");
        return proceedingJoinPoint.proceed();
    }
}
