package com.dzzdsj.demo.mybatisdemo.aop.aspect;

import com.dzzdsj.demo.mybatisdemo.annotation.routemap.EnableRouteMap;
import com.dzzdsj.demo.mybatisdemo.configuration.RouteMapConfig;
import com.dzzdsj.demo.mybatisdemo.configuration.RouteMapInfo;
import com.dzzdsj.demo.mybatisdemo.mapper.BaseRouteMapMapper;
import com.dzzdsj.demo.mybatisdemo.mapper.MapStudentCardNoSnameMapper;
import com.dzzdsj.demo.mybatisdemo.mapper.MapStudentMobileMapper;
import com.dzzdsj.demo.mybatisdemo.service.BaseRouteMapService;
import jakarta.annotation.Resource;
import org.apache.ibatis.session.SqlSession;
import org.apache.ibatis.session.SqlSessionFactory;
import org.aspectj.lang.ProceedingJoinPoint;
import org.aspectj.lang.annotation.Around;
import org.aspectj.lang.annotation.Aspect;
import org.aspectj.lang.annotation.Pointcut;
import org.aspectj.lang.reflect.MethodSignature;
import org.springframework.context.ApplicationContext;
import org.springframework.stereotype.Component;

import java.lang.reflect.Method;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Component
@Aspect
public class RouteMapAspect {
    @Resource
    private RouteMapConfig routeMapConfig;
    @Resource
    private MapStudentCardNoSnameMapper mapStudentCardNoSnameMapper;
    @Resource
    private MapStudentMobileMapper mapStudentMobileMapper;
    @Resource
    private BaseRouteMapService baseRouteMapService;
    @Resource
    private SqlSessionFactory sqlSessionFactory;
    @Pointcut("@annotation(enableRouteMap)")
    public void pointcutEnableRouteMap(EnableRouteMap enableRouteMap) {
    }

    @Around("pointcutEnableRouteMap(enableRouteMap)")
    public Object enableRouteMapAdvice(ProceedingJoinPoint proceedingJoinPoint, EnableRouteMap enableRouteMap) throws Throwable {
        System.out.println("=====================enableRouteMapAdvice=========================");
        String targetTable =  enableRouteMap.targetTable();
        String[] mapKeys = enableRouteMap.mapKeys();
        // 获取参数名称和值
        MethodSignature signature = (MethodSignature) proceedingJoinPoint.getSignature();
        Method method = signature.getMethod();
        String[] paramNames = signature.getParameterNames(); // 参数名数组
        Object[] args = proceedingJoinPoint.getArgs(); // 实参数组

        Map<String, Object> paramMap = new HashMap<>();
        for (int i = 0; i < paramNames.length; i++) {
            paramMap.put(paramNames[i], args[i]);
        }

        String key = targetTable + ":";
        for (String mapKey : mapKeys){
            key = key + mapKey + ",";
        }
        key = key.substring(0,key.length()-1);
        RouteMapInfo routeMapInfo = routeMapConfig.routeMapInfoMap.get(key);
        if(routeMapInfo != null){
            Class<?> routeMapperClass = routeMapInfo.getRouteMapperClass();
            String routeMapperMethod = routeMapInfo.getRouteMapperMethod();

            SqlSession sqlSession = sqlSessionFactory.openSession();
            BaseRouteMapMapper baseRouteMapMapper = (BaseRouteMapMapper) sqlSession.getMapper(routeMapperClass);
            List<String> shardkeys = baseRouteMapMapper.getShardkeys("s0001,Jerry");

            Class<?> targetMapperClass = routeMapInfo.getTargetMapperClass();
            String targetMapperMethod = routeMapInfo.getTargetMapperMethod();
        }
        return proceedingJoinPoint.proceed();
    }
}
