package com.dzzdsj.demo.springcloud.demoproject;

import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class ConsumerController {

    @RequestMapping(value = "/hello", method = RequestMethod.GET)
    public String helloConsumer(){
        return "hello";
    }
}
