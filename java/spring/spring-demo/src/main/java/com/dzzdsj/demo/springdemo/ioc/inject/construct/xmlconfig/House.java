package com.dzzdsj.demo.springdemo.ioc.inject.construct.xmlconfig;

import lombok.ToString;

@ToString
public class House {
    private int houseId;
    private Door door;

    public House(int houseId, Door door) {
        this.houseId = houseId;
        this.door = door;
    }
}
