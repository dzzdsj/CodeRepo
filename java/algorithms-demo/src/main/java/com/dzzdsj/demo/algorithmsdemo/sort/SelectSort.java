package com.dzzdsj.demo.algorithmsdemo.sort;

import com.dzzdsj.demo.algorithmsdemo.common.IntegerGenerator;
import com.dzzdsj.demo.algorithmsdemo.common.SortTamplate;

/**
 * 选择排序
 * 基本思想：从所有 n个元素中找到最小的一个元素，放到第1个位置(位置交换)
 * 从剩下的 n-1个元素中找到最小的一个元素，放到第2个位置(位置交换)
 * 。。。
 */
public class SelectSort implements SortTamplate {
    @Override
    public void sort(Comparable[] array) {
        for (int i = 0; i < array.length; i++) {
            System.out.println("outer loop " + "i=" + i);
            //最小元素的索引,每一轮先假定第i个元素为最小
            int minIndex = i;
            for (int j = i + 1; j < array.length; j++) {
//                System.out.println("    inner loop " + "i=" + i + ",j=" + j);
                if (less(array[j], array[minIndex])) {
                    minIndex = j;
                }
            }
            //将第i+1个之后的元素里的最小元素与第i个元素交换位置
            exchange(array, i, minIndex);
            show(array);
        }
    }

    public static void main(String[] args) {
        IntegerGenerator integerGenerator = new IntegerGenerator();
        Comparable[] comparables = integerGenerator.generateData(8);
        SelectSort selectSort = new SelectSort();
        System.out.println("======== before sort ======== ");
        selectSort.show(comparables);
        System.out.println("======== start sort ======== ");
        selectSort.sort(comparables);
        System.out.println("======== after sort ======== ");
        selectSort.show(comparables);
    }
}
/*
======== before sort ========
878 990 124 630 438 957 222 440
======== start sort ========
round 0
124 990 878 630 438 957 222 440
round 1
124 222 878 630 438 957 990 440
round 2
124 222 438 630 878 957 990 440
round 3
124 222 438 440 878 957 990 630
round 4
124 222 438 440 630 957 990 878
round 5
124 222 438 440 630 878 990 957
round 6
124 222 438 440 630 878 957 990
round 7
124 222 438 440 630 878 957 990
 */