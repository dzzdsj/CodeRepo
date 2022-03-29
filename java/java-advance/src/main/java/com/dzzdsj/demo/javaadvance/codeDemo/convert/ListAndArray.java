package com.dzzdsj.demo.javaadvance.codeDemo.convert;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;

public  class ListAndArray {
    private List<String> arrayToList(String[] strArr) {
        List<String> list = new ArrayList<>();
        Collections.addAll(list, strArr);
        return list;
    }

    private List<String> arrayToList2(String[] strArr) {
        //该方法的返回值是java.util.Arrays类中一个私有静态内部类java.util.Arrays.ArrayList，
        //它并非java.util.ArrayList类。
        //java.util.Arrays.ArrayList类具有set()，get()，contains()等方法，
        //但是不支持添加add()或删除remove()方法,调用这些方法会报错

//        如果仅仅为了打印数组，不需要把数组转换成List，可以使用Arrays.toString()方法。
        return Arrays.asList(strArr);
    }


    public static void main(String[] args) {
        ListAndArray listAndArray = new ListAndArray();
        String[] strArr = {"1","2","3"};
        List<String> list = listAndArray.arrayToList(strArr);
        System.out.println("list="+ list);
        list.add("4");
        System.out.println("list="+ list);

        List<String> list2 = listAndArray.arrayToList2(strArr);
        System.out.println("list2="+ list2);

        //java.lang.UnsupportedOperationException
        list2.add("4");
        System.out.println("list2="+ list2);
    }
}
