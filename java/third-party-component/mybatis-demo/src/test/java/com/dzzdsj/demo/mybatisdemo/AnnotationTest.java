package com.dzzdsj.demo.mybatisdemo;

import com.dzzdsj.demo.mybatisdemo.annotation.ClassAnnotation;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.config.BeanDefinition;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.context.annotation.ClassPathScanningCandidateComponentProvider;
import org.springframework.core.io.Resource;
import org.springframework.core.io.support.PathMatchingResourcePatternResolver;
import org.springframework.core.type.classreading.MetadataReader;
import org.springframework.core.type.classreading.MetadataReaderFactory;
import org.springframework.core.type.classreading.SimpleMetadataReaderFactory;
import org.springframework.core.type.filter.AnnotationTypeFilter;

import java.io.IOException;
import java.util.Set;

@SpringBootTest
public class AnnotationTest {

    @Test
    void getMyAnnotation() {
        //只会扫描类，无法扫描接口
        ClassPathScanningCandidateComponentProvider scanner = new ClassPathScanningCandidateComponentProvider(false);
        scanner.addIncludeFilter(new AnnotationTypeFilter(ClassAnnotation.class));
        Set<BeanDefinition> beanDefinitions = scanner.findCandidateComponents("com.dzzdsj.demo");
        beanDefinitions.forEach(e -> {
            System.out.println(e.getBeanClassName());
        });
    }

    @Test
    void scanInterfacesWithAnnotation() throws IOException {
        PathMatchingResourcePatternResolver resolver = new PathMatchingResourcePatternResolver();
        Resource[] resources = resolver.getResources("classpath:com/dzzdsj/demo/**/*.class");

        MetadataReaderFactory readerFactory = new SimpleMetadataReaderFactory();
        AnnotationTypeFilter filter = new AnnotationTypeFilter(ClassAnnotation.class);

        for (Resource resource : resources) {
            MetadataReader reader = readerFactory.getMetadataReader(resource);
            if (filter.match(reader, readerFactory)) {
                String className = reader.getClassMetadata().getClassName();
                System.out.println("Found annotated interface or class: " + className);
            }
        }
    }
}
