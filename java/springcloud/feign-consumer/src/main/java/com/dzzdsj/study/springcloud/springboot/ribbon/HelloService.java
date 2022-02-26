package com.dzzdsj.study.springcloud.springboot.ribbon;

import org.springframework.cloud.netflix.feign.FeignClient;
import org.springframework.web.bind.annotation.*;

@FeignClient("hello-service") //指定服务名来绑定服务，不区分大小写,同时会创建同名的ribbon客户端，
                              // 可以在yml配置中指定配置
public interface HelloService {

    @RequestMapping("/hello")
    String hello();

    //使用feign时，注解里的value不可少
    @RequestMapping(value = "/hello1", method = RequestMethod.GET)
    String hello(@RequestParam(value = "name") String name) ;


    @RequestMapping(value = "/hello2", method = RequestMethod.GET)
    User hello(@RequestHeader("name") String name, @RequestHeader("age") Integer age) ;


    @RequestMapping(value = "/hello3", method = RequestMethod.POST)
    String hello(@RequestBody User user) ;

}
