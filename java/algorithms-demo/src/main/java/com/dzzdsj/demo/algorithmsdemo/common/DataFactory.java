package com.dzzdsj.demo.algorithmsdemo.common;

import java.util.Random;

public abstract class DataFactory {
    private Integer[] data;

    public void genData(int size) {
        data = new Integer[size];
        Random random = new Random();
        for (int i = 0; i < data.length; i++) {
            data[i] = random.nextInt(900) + 100;
        }
    }

    public Integer[] getData() {
        return data;
    }

    public void setData(Integer[] data) {
        this.data = data;
    }
}
