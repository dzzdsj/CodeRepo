package com.dzzdsj.demo.algorithmsdemo.sort;

import com.dzzdsj.demo.algorithmsdemo.common.IntegerGenerator;
import com.dzzdsj.demo.algorithmsdemo.common.SortTamplate;

/**
 * 插入排序
 * 基本原理：从第array[1]开始，将元素插入到它之前元素的合适位置
 *          外层循环i轮后，则前i个元素已经有序了。
 *
 * 特点：（shell排序将数组分组拆小，才能发挥插入排序的优势）
 * 1. 当待排序的原序列中大多数元素都已有序的情况下，此时进行的元素比较和移动的次数较少；
 * 2. 当原序列的长度很小时，即便它的所有元素都是无序的，此时进行的元素比较和移动的次数还是很少。
 */
public class InsertSort implements SortTamplate {

    public void sort(Comparable[] array) {
        for (int i = 1; i < array.length; i++) {
            System.out.println("outer loop " + "i=" + i);
            for (int j = i; j > 0 && less(array[j], array[j - 1]); j--) {
                System.out.println("    inner loop " + "i=" + i + ",j=" + j);
                //将第i个元素里插入到它之前的元素中（i之前的都有序了）
                //为了给待插入的元素腾地方，这里的做法是从第i个元素开始，依次与它的前一个元素做比较，发现比它小就交换位置
                //直到到达它的合适的位置
                exchange(array, j, j - 1);
                show(array);
            }
        }
    }


    public static void main(String[] args) {
        IntegerGenerator integerGenerator = new IntegerGenerator();
        Comparable[] comparables = integerGenerator.generateData(8);
        InsertSort InsertSort = new InsertSort();
        System.out.println("======== before sort ======== ");
        InsertSort.show(comparables);
        System.out.println("======== start sort ======== ");
        InsertSort.sort(comparables);
        System.out.println("======== after sort ======== ");
        InsertSort.show(comparables);
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