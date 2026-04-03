package com.dzzdsj.junitdemo;

public class SUT {
    public SUT() {
    }

    public SUT(String description) {
        System.out.println("Creating SUT: " + description);
    }

    public boolean canReceiveRegularWork() {
        return true;
    }
    public boolean canReceiveAdditionalWork() {
        return true;
    }

    public void close() {
        System.out.println("Closing SUT");
    }

    public String hello() {
        return "Hello";
    }

}
