package com.dzzdsj.demo.mybatisdemo.controller;

import com.dzzdsj.demo.mybatisdemo.annotation.ClassAnnotation;
import com.dzzdsj.demo.mybatisdemo.annotation.MethodAnnotation;
import org.springframework.core.io.Resource;
import org.springframework.core.io.support.PathMatchingResourcePatternResolver;
import org.springframework.core.type.classreading.MetadataReader;
import org.springframework.core.type.classreading.MetadataReaderFactory;
import org.springframework.core.type.classreading.SimpleMetadataReaderFactory;
import org.springframework.core.type.filter.AnnotationTypeFilter;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.io.IOException;
import java.lang.annotation.Annotation;
import java.lang.reflect.Method;

@RestController()
@RequestMapping("/test")
public class TestController {
    @GetMapping("/test")
    public void scanInterfacesWithAnnotation() throws IOException {
        PathMatchingResourcePatternResolver resolver = new PathMatchingResourcePatternResolver();
        Resource[] resources = resolver.getResources("classpath:com/dzzdsj/demo/**/*.class");

        MetadataReaderFactory readerFactory = new SimpleMetadataReaderFactory();
        AnnotationTypeFilter filter = new AnnotationTypeFilter(ClassAnnotation.class);

        for (Resource resource : resources) {
            MetadataReader reader = readerFactory.getMetadataReader(resource);
            if (filter.match(reader, readerFactory)) {
                String className = reader.getClassMetadata().getClassName();
                System.out.println("Found annotated interface or class: " + className);
                try {
                    Class<?> clazz = Class.forName(className);
                    Annotation annotation = clazz.getAnnotation(ClassAnnotation.class);
                    String value = ((ClassAnnotation) annotation).value();
                    if(value != null){
                        System.out.println("Annotation value: " + value);
                    }
                    Method[] methods = clazz.getMethods();
                    for (Method method : methods) {
                        Annotation methodAnnotation = method.getAnnotation(MethodAnnotation.class);
                        if (methodAnnotation != null) {
                            String methodValue = ((MethodAnnotation) methodAnnotation).value();
                            System.out.println("Method annotation value: " + methodValue);
                        }
                    }
                } catch (ClassNotFoundException e) {
                    throw new RuntimeException(e);
                }
            }
        }
    }
}
