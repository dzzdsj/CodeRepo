package com.dzzdsj.demo.springdemo.ioc.inject.construct.xmlconfig;

import lombok.Data;

@Data
public class Door {
    private int id;
    private String productAddress;

    public int getId() {
        return id;
    }

    public void setId(int id) {
        this.id = id;
    }

    public String getProductAddress() {
        return productAddress;
    }

    public void setProductAddress(String productAddress) {
        this.productAddress = productAddress;
    }
}
