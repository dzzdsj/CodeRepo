package com.dzzdsj.demo.algorithmsdemo.common;

public interface SortTamplate {
    void sort(Comparable[] arrays);

    default boolean less(Comparable v, Comparable w) {
        return v.compareTo(w) < 0;
    };

    default void exchange(Comparable[] array, int i, int j){
        Comparable temp = array[i];
        array[i] = array[j];
        array[j] = temp;
    };

    default void show(Comparable[] array){
        for (int i = 0; i < array.length; i++) {
            System.out.print(array[i] +"[" + i + "]" + " ");
        }
        System.out.println();
    };

    default boolean isSorted(Comparable[] array){
        for (int i = 0; i < array.length; i++) {
            if (less(array[i], array[i - 1])) {
                return false;
            }
        }
        return true;
    };

}
