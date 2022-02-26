package com.dzzdsj.study.springcloud.springboot.ribbon;

import com.netflix.hystrix.contrib.javanica.annotation.HystrixCommand;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

@Service
public class ConsumerService {
    @Autowired
    private RestTemplate restTemplate;

    //指定熔断后回调方法,依赖的服务返回单个结果时使用
    @HystrixCommand(fallbackMethod = "helloFallBack")
    public String helloService(){
        String result = restTemplate.getForEntity("http://HELLO-SERVICE/hello",String.class).getBody();
        return result;
    }

    public String helloFallBack(){
        return "error";
    }
}
