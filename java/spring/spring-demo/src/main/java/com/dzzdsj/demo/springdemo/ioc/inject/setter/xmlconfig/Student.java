package com.dzzdsj.demo.springdemo.ioc.inject.setter.xmlconfig;

import lombok.Data;

@Data
public class Student {
    String name;
    Integer age;
    IDCard idCard;

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public Integer getAge() {
        return age;
    }

    public void setAge(Integer age) {
        this.age = age;
    }

    public IDCard getIdCard() {
        return idCard;
    }

    public void setIdCard(IDCard idCard) {
        this.idCard = idCard;
    }
}
