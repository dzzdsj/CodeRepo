package com.dzzdsj.demo.springcloud2020.service;

import com.dzzdsj.demo.springcloud2020.entity.Payment;
import org.apache.ibatis.annotations.Param;

public interface PaymentService {
    int create(Payment payment);

    Payment getPaymentById(@Param("id") Long id);
}
