package com.dzzdsj.demo.mybatisdemo.configuration;

import com.dzzdsj.demo.mybatisdemo.annotation.routemap.RouteMap;
import com.dzzdsj.demo.mybatisdemo.annotation.routemap.RouteMapMapper;
import jakarta.annotation.PostConstruct;
import org.springframework.context.annotation.Configuration;
import org.springframework.core.io.Resource;
import org.springframework.core.io.support.PathMatchingResourcePatternResolver;
import org.springframework.core.type.classreading.MetadataReader;
import org.springframework.core.type.classreading.MetadataReaderFactory;
import org.springframework.core.type.classreading.SimpleMetadataReaderFactory;
import org.springframework.core.type.filter.AnnotationTypeFilter;

import java.io.IOException;
import java.lang.reflect.Method;
import java.util.Map;
@Configuration
public class RouteMapConfig {
    public static final Map<String,RouteMapInfo> routeMapInfoMap = new java.util.HashMap<>();
    @PostConstruct
    public void init(){
        scanInterfacesWithAnnotation();
        System.out.println(routeMapInfoMap);
    }

    private static void scanInterfacesWithAnnotation() {
        try {
            PathMatchingResourcePatternResolver resolver = new PathMatchingResourcePatternResolver();
            Resource[] resources = resolver.getResources("classpath:com/dzzdsj/demo/mybatisdemo/**/*.class");

            MetadataReaderFactory readerFactory = new SimpleMetadataReaderFactory();
            AnnotationTypeFilter filter = new AnnotationTypeFilter(RouteMapMapper.class);

            for (Resource resource : resources) {
                MetadataReader reader = readerFactory.getMetadataReader(resource);
                if (filter.match(reader, readerFactory)) {
                    String className = reader.getClassMetadata().getClassName();
                    System.out.println("Found annotated interface or class: " + className);
                    Class<?> clazz = Class.forName(className);
                    if(clazz.isAnnotationPresent(RouteMapMapper.class)){
                        RouteMapMapper routeMapMapper = clazz.getAnnotation(RouteMapMapper.class);
                        String targetTable = routeMapMapper.targetTable();
                        String[] mapKeys = routeMapMapper.mapKeys();
                        String key = targetTable + ":";
                        for (String mapKey : mapKeys) {
                            key = key + mapKey + ",";
                        }
                        key = key.substring(0, key.length() - 1);

                        Method[] methods = clazz.getMethods();
                        for (Method method : methods) {
                            if(method.isAnnotationPresent(RouteMap.class)){
                                RouteMapInfo routeMapInfo = new RouteMapInfo();
                                routeMapInfo.setRouteMapperClass(routeMapMapper.routeMapperClass());
                                RouteMap routeMap = method.getAnnotation(RouteMap.class);
                                routeMapInfo.setRouteMapperMethod(routeMap.routeMapMethod());
                                routeMapInfo.setTargetMapperClass(routeMap.targetClass());
                                routeMapInfo.setTargetMapperMethod(routeMap.targetMethod());
                                routeMapInfoMap.put(key,routeMapInfo);
                            }
                        }
                    }
                }
            }
        }catch (IOException e){
            e.printStackTrace();
        }catch (ClassNotFoundException e){
            e.printStackTrace();
        }
    }
}
