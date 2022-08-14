package com.dzzdsj.demo.algorithmsdemo.sort;

import com.dzzdsj.demo.algorithmsdemo.common.DataFactory;
import com.dzzdsj.demo.algorithmsdemo.common.SortTamplate;

/**
 * 插入排序
 */
public class InsertSort extends DataFactory implements SortTamplate {

    public  void sort(Comparable[] array) {
        for (int i = 1; i < array.length; i++) {
            System.out.println("round " + i);
            for (int j = i ; j > 0 && less(array[j], array[j-1]); j--) {
                //将第i个元素里插入到它之前的元素中（i之前的都有序了）
                //为了给待插入的元素腾地方，这里的做法是从第i个元素开始，依次与它的前一个元素做比较，发现比它小就交换位置
                //直到到达它的合适的位置
                exchange(array, j, j-1);
                show(array);
            }
            show(array);
        }
    }

    public  boolean less(Comparable v, Comparable w) {
        return v.compareTo(w) < 0;
    }

    public  void exchange(Comparable[] array, int i, int j) {
        Comparable temp = array[i];
        array[i] = array[j];
        array[j] = temp;
    }

    public  void show(Comparable[] array) {
        for (int i = 0; i < array.length; i++) {
            System.out.print(array[i] + " ");
        }
        System.out.println();
    }

    public  boolean isSorted(Comparable[] array) {
        for (int i = 0; i < array.length; i++) {
            if (less(array[i], array[i - 1])) {
                return false;
            }
        }
        return true;
    }

    public static void main(String[] args) {
        InsertSort data = new InsertSort();
//        data.genData(Integer.valueOf(args[0]));
        data.genData(10);
        System.out.println("======== before sort ======== ");
        data.show(data.getData());
        System.out.println("======== start sort ======== ");
        data.sort(data.getData());
    }
}
/*
======== before sort ========
180 563 198 212 409 289 896 454 832 967
======== start sort ========
round 1
180 563 198 212 409 289 896 454 832 967
round 2
180 198 563 212 409 289 896 454 832 967
180 198 563 212 409 289 896 454 832 967
round 3
180 198 212 563 409 289 896 454 832 967
180 198 212 563 409 289 896 454 832 967
round 4
180 198 212 409 563 289 896 454 832 967
180 198 212 409 563 289 896 454 832 967
round 5
180 198 212 409 289 563 896 454 832 967
180 198 212 289 409 563 896 454 832 967
180 198 212 289 409 563 896 454 832 967
round 6
180 198 212 289 409 563 896 454 832 967
round 7
180 198 212 289 409 563 454 896 832 967
180 198 212 289 409 454 563 896 832 967
180 198 212 289 409 454 563 896 832 967
round 8
180 198 212 289 409 454 563 832 896 967
180 198 212 289 409 454 563 832 896 967
round 9
180 198 212 289 409 454 563 832 896 967 
 */