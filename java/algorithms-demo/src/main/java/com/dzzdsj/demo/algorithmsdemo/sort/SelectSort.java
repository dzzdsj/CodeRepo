package com.dzzdsj.demo.algorithmsdemo.sort;

import com.dzzdsj.demo.algorithmsdemo.common.DataFactory;
import com.dzzdsj.demo.algorithmsdemo.common.SortTamplate;

/**
 * 选择排序
 */
public class SelectSort extends DataFactory implements SortTamplate {

    public  void sort(Comparable[] array) {
        for (int i = 0; i < array.length; i++) {
            System.out.println("round " + i);
            //最小元素的索引,每一轮先假定第i个元素为最小
            int minIndex = i;
            for (int j = i + 1; j < array.length; j++) {
                if (less(array[j], array[minIndex])){
                    minIndex = j;
                }
            }
            //将第i+1个之后的元素里的最小元素与第i个元素交换位置
            exchange(array, i, minIndex);
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
        SelectSort data = new SelectSort();
//        data.genData(Integer.valueOf(args[0]));
        data.genData(8);
        System.out.println("======== before sort ======== ");
        data.show(data.getData());
        System.out.println("======== start sort ======== ");
        data.sort(data.getData());
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