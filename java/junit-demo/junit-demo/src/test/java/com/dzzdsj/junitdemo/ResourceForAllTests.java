package com.dzzdsj.junitdemo;

public class ResourceForAllTests {
    public ResourceForAllTests(String description) {
        System.out.println("ResourceForAllTests: " + description);
    }

    public void close() {
        System.out.println("Closing ResourceForAllTests");
    }
}
