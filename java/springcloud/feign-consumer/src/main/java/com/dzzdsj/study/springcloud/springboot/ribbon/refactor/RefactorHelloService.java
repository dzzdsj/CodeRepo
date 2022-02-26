package com.dzzdsj.study.springcloud.springboot.ribbon.refactor;

import com.dzzdsj.study.springcloud.springboot.hello.service.HelloService;
import org.springframework.cloud.netflix.feign.FeignClient;

@FeignClient("hello-service") //指定服务名来绑定服务，不区分大小写
public interface RefactorHelloService extends HelloService {



}
