package com.dzzdsj.demo.algorithmsdemo.common;

import java.util.Random;

public class IntegerGenerator implements DataGenerator {

    @Override
    public Comparable[] generateData(int size) {
        Random random = new Random();
        Integer[] array = new Integer[size];
        for (int i = 0; i < array.length; i++) {
            array[i] = random.nextInt(900) + 100;
        }
        return array;
    }
}
