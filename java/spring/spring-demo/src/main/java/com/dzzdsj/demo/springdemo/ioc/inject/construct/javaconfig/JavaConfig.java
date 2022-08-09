package com.dzzdsj.demo.springdemo.ioc.inject.construct.javaconfig;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.ComponentScan;
import org.springframework.context.annotation.Configuration;

//@Configuration注解作用相当于xml配置文件
@Configuration
//ComponentScan会扫描包下带有@Component、@Service、@Controller、@Repository的注解的类，将它们注册为Bean
@ComponentScan("com.dzzdsj.demo.springdemo.ioc.inject.construct.javaconfig")
public class JavaConfig {
//    @Bean
//    public Car car() {
//        Car car = new Car(this.window());
//        return car;
//    }
//
//    @Bean
//    public Window window() {
//        Window window = new Window();
//        window.setId(100);
//        window.setName("abd");
//        return window;
//    }
}
