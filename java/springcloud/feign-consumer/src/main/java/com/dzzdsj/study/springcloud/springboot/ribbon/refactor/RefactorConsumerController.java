package com.dzzdsj.study.springcloud.springboot.ribbon.refactor;

import com.dzzdsj.study.springcloud.springboot.hello.dto.User;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class RefactorConsumerController {
    @Autowired
    private RefactorHelloService refactorHelloService;

    @RequestMapping(value = "/feign-consumer3", method = RequestMethod.GET)
    public String helloConsumer3(){
        StringBuilder sb = new StringBuilder();
//        sb.append(refactorHelloService.hello()).append("\n");
        sb.append(refactorHelloService.hello("DIDI")).append("\n");
        sb.append(refactorHelloService.hello("DIDI", 6)).append("\n");
        sb.append(refactorHelloService.hello(new User("DIDI", 6))).append("\n");
        return sb.toString();
    }
}
