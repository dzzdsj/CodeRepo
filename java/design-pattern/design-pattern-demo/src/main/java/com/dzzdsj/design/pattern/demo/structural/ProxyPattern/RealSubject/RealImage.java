package com.dzzdsj.design.pattern.demo.structural.ProxyPattern.RealSubject;

import com.dzzdsj.design.pattern.demo.structural.ProxyPattern.Subject.Image;

public class RealImage implements Image {

    private String fileName;

    public RealImage(String fileName) {
        this.fileName = fileName;
        loadFromDisk(fileName);
    }

    @Override
    public void display() {
        System.out.println("Displaying " + fileName);
    }

    private void loadFromDisk(String fileName) {
        System.out.println("Loading " + fileName);
    }
}
