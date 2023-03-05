package com.dzzdsj.demo.algorithmsdemo.sort;

import com.dzzdsj.demo.algorithmsdemo.common.IntegerGenerator;
import com.dzzdsj.demo.algorithmsdemo.common.SortTamplate;

/**
 * 插入排序
 * 基本原理：从第array[1]开始，将元素插入到它之前元素的合适位置
 * 外层循环i轮后，则前i个元素已经有序了。
 */
public class ShellSort implements SortTamplate {

    public void sort(Comparable[] array) {
        int size = array.length;
        int h = 1;
        while (h < size / 3) {
            h = 3 * h + 1;
        }
        while (h >= 1) {
            System.out.println("outer loop h=" + h);
            for (int i = h; i < size; i++) {
                System.out.println("    middle loop " + "i=" + i + ",h=" + h);
                for (int j = i; j >= h && less(array[j], array[j - h]); j -= h) {
                    System.out.println("        inner loop " + "i=" + i + ",h=" + h + ",j=" + j);
                    exchange(array, j, j - h);
                    show(array);
                }
            }
            h = h / 3;
        }
    }


    public static void main(String[] args) {
        IntegerGenerator integerGenerator = new IntegerGenerator();
        Comparable[] comparables = integerGenerator.generateData(20);
        ShellSort shellSort = new ShellSort();
        System.out.println("======== before sort ======== ");
        shellSort.show(comparables);
        System.out.println("======== start sort ======== ");
        shellSort.sort(comparables);
        System.out.println("======== after sort ======== ");
        shellSort.show(comparables);
    }
}
/*

 */