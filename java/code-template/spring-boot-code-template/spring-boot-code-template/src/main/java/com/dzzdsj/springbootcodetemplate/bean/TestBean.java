package com.dzzdsj.springbootcodetemplate.bean;

import lombok.Data;
import org.springframework.stereotype.Component;

@Component
@Data
public class TestBean {
    private Integer id = 1;
    private String name = "testbean";
}
