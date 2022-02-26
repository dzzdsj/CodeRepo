package com.dzzdsj.study.springcloud.springboot.hello.refactor;

import com.dzzdsj.study.springcloud.springboot.hello.dto.User;
import com.dzzdsj.study.springcloud.springboot.hello.service.HelloService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.cloud.client.ServiceInstance;
import org.springframework.cloud.client.discovery.DiscoveryClient;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.Random;
import java.util.concurrent.TimeUnit;

@RestController
public class RefactorHelloController implements HelloService {
    @Autowired
    private DiscoveryClient discoveryClient; // 服务发现客户端

    @Override
    public String hello(){
        ServiceInstance serviceInstance = discoveryClient.getLocalServiceInstance();
        try {
            //hystrix 默认超时时间是2000ms，指定3000内随机数，概率性触发熔断
            int sleepTime = new Random().nextInt(3000);
            TimeUnit.MILLISECONDS.sleep(sleepTime);
            System.out.println("sleepTime=" + sleepTime);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        return serviceInstance.toString();
    }

    @Override
    public String hello(@RequestParam String name) {
        return "hello"+ name;
    }

    @Override
    public User hello(@RequestHeader String name, @RequestHeader Integer age) {
        return new User(name, age);
    }

    @Override
    public String hello(@RequestBody User user) {
        return "hello"+ user.getName() + "," + user.getAge();
    }
}
