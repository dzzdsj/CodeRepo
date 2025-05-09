package com.dzzdsj.demo.mybatisdemo.aop.aspect;

import com.dzzdsj.demo.mybatisdemo.annotation.routemap.EnableRouteMap;
import com.dzzdsj.demo.mybatisdemo.configuration.RouteMapConfig;
import com.dzzdsj.demo.mybatisdemo.configuration.RouteMapInfo;
import com.dzzdsj.demo.mybatisdemo.mapper.BaseMapper;
import com.dzzdsj.demo.mybatisdemo.mapper.BaseRouteMapMapper;
import com.dzzdsj.demo.mybatisdemo.mapper.MapStudentCardNoSnameMapper;
import com.dzzdsj.demo.mybatisdemo.mapper.MapStudentMobileMapper;
import com.dzzdsj.demo.mybatisdemo.service.BaseRouteMapService;
import com.dzzdsj.demo.mybatisdemo.service.BaseService;
import com.dzzdsj.demo.mybatisdemo.utils.NamingConverter;
import jakarta.annotation.Resource;
import org.apache.ibatis.session.SqlSession;
import org.apache.ibatis.session.SqlSessionFactory;
import org.aspectj.lang.ProceedingJoinPoint;
import org.aspectj.lang.annotation.Around;
import org.aspectj.lang.annotation.Aspect;
import org.aspectj.lang.annotation.Pointcut;
import org.aspectj.lang.reflect.MethodSignature;
import org.springframework.stereotype.Component;

import java.lang.reflect.Method;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Component
@Aspect
public class RouteMapAspect {
    @Resource
    private RouteMapConfig routeMapConfig;
    @Resource
    private BaseRouteMapService baseRouteMapService;
    @Resource
    private SqlSessionFactory sqlSessionFactory;
    @Resource
    private BaseService baseService;

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

        String argsString = getArgsString(mapKeys,paramMap);
        System.out.println("argsString: " + argsString);

        RouteMapInfo routeMapInfo = routeMapConfig.routeMapInfoMap.get(key);
        if(routeMapInfo != null){
            Class<?> routeMapperClass = routeMapInfo.getRouteMapperClass();
            String routeMapperMethod = routeMapInfo.getRouteMapperMethod();
//方式一：使用 sqlSessionFactory.openSession()获取mapper
            SqlSession sqlSession = sqlSessionFactory.openSession();
            BaseRouteMapMapper baseRouteMapMapper = (BaseRouteMapMapper) sqlSession.getMapper(routeMapperClass);
//            List<?> shardKeys = baseRouteMapMapper.getShardkeys(argsString);
//            if(shardKeys.size()  != 0){
//                Class<?> targetMapperClass = routeMapInfo.getTargetMapperClass();
//                String targetMapperMethod = routeMapInfo.getTargetMapperMethod();
//
//                BaseMapper baseMapper = (BaseMapper) sqlSession.getMapper(targetMapperClass);
//                List<?> resultList = baseMapper.queryByShardKeys(shardKeys);
//                System.out.println(resultList);
//                return resultList;
//            }
//方式二：使用service方法
            List<?> shardKeys = baseRouteMapService.getShardkeys(baseRouteMapMapper, argsString);
            if(shardKeys.size()  != 0){
                Class<?> targetMapperClass = routeMapInfo.getTargetMapperClass();
                String targetMapperMethod = routeMapInfo.getTargetMapperMethod();

                BaseMapper baseMapper = (BaseMapper) sqlSession.getMapper(targetMapperClass);
                List<?> resultList = baseService.queryByShardKeys(baseMapper, shardKeys);
                System.out.println(resultList);
                return resultList;
            }
        }
        return proceedingJoinPoint.proceed();
    }
    private String getArgsString(String[] mapKeys,Map<String,Object> paramMap){
        StringBuilder sb = new StringBuilder();
        for (String mapKey : mapKeys){
            mapKey = NamingConverter.underlineToCamel(mapKey);
            if(paramMap.get(mapKey) != null){
                sb.append(paramMap.get(mapKey)).append(",");
            }
        }
        sb.deleteCharAt(sb.length()-1);
        return sb.toString();
    }
}
