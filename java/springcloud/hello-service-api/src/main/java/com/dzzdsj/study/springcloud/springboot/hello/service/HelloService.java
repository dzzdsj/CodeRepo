package com.dzzdsj.study.springcloud.springboot.hello.service;

import com.dzzdsj.study.springcloud.springboot.hello.dto.User;
import org.springframework.web.bind.annotation.*;

@RequestMapping("/refactor")
public interface HelloService {
    @RequestMapping("/hello")
    String hello();

    //使用feign时，注解里的value不可少
    @RequestMapping(value = "/hello4", method = RequestMethod.GET)
    String hello(@RequestParam(value = "name") String name) ;


    @RequestMapping(value = "/hello5", method = RequestMethod.GET)
    User hello(@RequestHeader("name") String name, @RequestHeader("age") Integer age) ;


    @RequestMapping(value = "/hello6", method = RequestMethod.POST)
    String hello(@RequestBody User user) ;
}
