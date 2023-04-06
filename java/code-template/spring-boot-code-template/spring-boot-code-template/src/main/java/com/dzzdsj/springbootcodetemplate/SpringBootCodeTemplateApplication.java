package com.dzzdsj.springbootcodetemplate;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.ComponentScan;
import org.springframework.context.annotation.ImportResource;


@SpringBootApplication
//Indicates one or more resources containing bean definitions to import
@ImportResource(locations = "classpath:beans.xml")
public class SpringBootCodeTemplateApplication {

    public static void main(String[] args) {
        SpringApplication.run(SpringBootCodeTemplateApplication.class, args);
    }

}
