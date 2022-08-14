package com.dzzdsj.demo.algorithmsdemo.common;

public interface SortTamplate {
    void sort(Comparable[] array);

    boolean less(Comparable v, Comparable w);

    void exchange(Comparable[] array, int i, int j);

    void show(Comparable[] array);

    boolean isSorted(Comparable[] array);

}
