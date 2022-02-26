package com.dzzdsj.study.springcloud.springboot.hello;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.cloud.client.ServiceInstance;
import org.springframework.cloud.client.discovery.DiscoveryClient;
import org.springframework.web.bind.annotation.*;

import java.util.Random;
import java.util.concurrent.TimeUnit;

@RestController
public class HelloController {
    @Autowired
    private DiscoveryClient discoveryClient; // 服务发现客户端


    @RequestMapping(value = "/hello", method = RequestMethod.GET)
    public ServiceInstance hello(){
        ServiceInstance serviceInstance = discoveryClient.getLocalServiceInstance();
        try {
            //hystrix 默认超时时间是2000ms，指定3000内随机数，概率性触发熔断
            int sleepTime = new Random().nextInt(1000);
            TimeUnit.MILLISECONDS.sleep(sleepTime);
            System.out.println("sleepTime=" + sleepTime);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        return serviceInstance;
    }

    @RequestMapping(value = "/hello1", method = RequestMethod.GET)
    public String hello(@RequestParam String name) {
        return "hello"+ name;
    }

    @RequestMapping(value = "/hello2", method = RequestMethod.GET)
    public User hello(@RequestHeader String name, @RequestHeader Integer age) {
        return new User(name, age);
    }

    @RequestMapping(value = "/hello3", method = RequestMethod.POST)
    public String hello(@RequestBody User user) {
        return "hello"+ user.getName() + "," + user.getAge();
    }
}
