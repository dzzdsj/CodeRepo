package com.dzzdsj.demo.algorithmsdemo.sort;

import com.dzzdsj.demo.algorithmsdemo.common.IntegerGenerator;
import com.dzzdsj.demo.algorithmsdemo.common.SortTamplate;

/**
 * 希尔排序
 * 基本原理：是插入排序的改进，将待排序数组拆分为h（增量）组，再对h组数据进行插入排序。再减小h，进行多轮
 *          好处是减少了每次插入排序的数组大小，同时多次操作后，数组整体已经基本有序了
 */
public class ShellSort implements SortTamplate {

    public void sort(Comparable[] array) {
        int size = array.length;
        int h = 1;
        while (h < size / 3) {
            h = 3 * h + 1;
        }
//        外层循环，控制排序的趟数
        while (h >= 1) {
            System.out.println("outer loop h=" + h);
//            整个数组分为h个子序列。其中第0~h-1个元素分属于不同的子序列。
//            中间层循环，顺序遍历整个数组每个元素，每遍历到一个元素，就对在它所属的子序列对它进行插入排序
            for (int i = h; i < size; i++) {
                System.out.println("    middle loop " + "i=" + i + ",h=" + h);
//                内层循环，进行插入排序，这里是位置j和j-h比较,而不是j和j-1，只有这样才能使数组整体有序，
//                比较的位置是h，2h，3h....nh
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