package com.dzzdsj.demo.springcloud2020.controller;

import com.dzzdsj.demo.springcloud2020.entity.CommonResult;
import com.dzzdsj.demo.springcloud2020.entity.Payment;
import com.dzzdsj.demo.springcloud2020.service.PaymentService;
import lombok.extern.slf4j.Slf4j;
import org.springframework.web.bind.annotation.*;

import javax.annotation.Resource;

@RestController
@Slf4j
public class PaymentController {
//    private Logger logger = LoggerFactory.getLogger(PaymentController.class);
    @Resource
    private PaymentService paymentService;

    @PostMapping(value = "/payment/create")
    public CommonResult create(@RequestBody Payment payment) {
        int result = paymentService.create(payment);
        log.info("*****插入结果：" + result);
        if(result > 0){
            return new CommonResult(200, "插入数据成功", result);
        }else {
            return new CommonResult(444, "插入数据失败", null);
        }
    }

    @GetMapping(value = "/payment/get/{id}")
    public CommonResult<Payment> getPaymentById(@PathVariable("id") Long id) {
        Payment payment = paymentService.getPaymentById(id);
        log.info("*****查询成功：" + payment);
        if(payment != null){
            return new CommonResult(200, "查询成功", payment);
        }else {
            return new CommonResult(444, "没有对应记录，查询id：" + id, null);
        }
    }
}
