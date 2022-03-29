package com.dzzdsj.demo.javaadvance.javaSE.annotation;
@MyAnnotation(name = "ClassWithAnnotation",score = {1,3})
public class WithAnnotation {
    private String name;
    private Integer age;
    private Integer[] score;
    public int myAge(){
        return this.age;
    }
}
