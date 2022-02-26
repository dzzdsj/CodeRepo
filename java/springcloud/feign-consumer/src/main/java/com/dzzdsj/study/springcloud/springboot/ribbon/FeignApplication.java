package com.dzzdsj.study.springcloud.springboot.ribbon;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cloud.client.circuitbreaker.EnableCircuitBreaker;
import org.springframework.cloud.client.discovery.EnableDiscoveryClient;
import org.springframework.cloud.netflix.feign.EnableFeignClients;

//@SpringCloudApplication  //包含了以下三个注解
@EnableDiscoveryClient
@SpringBootApplication
@EnableCircuitBreaker //开启断路器功能
@EnableFeignClients  //开启feign客户端
public class FeignApplication {
//    @Bean
//    @LoadBalanced //开启客户端负载均衡
//    RestTemplate restTemplate(){
//        return new RestTemplate();
//    }

    public static void main(String[] args) {
        SpringApplication.run(FeignApplication.class, args);
    }
}
