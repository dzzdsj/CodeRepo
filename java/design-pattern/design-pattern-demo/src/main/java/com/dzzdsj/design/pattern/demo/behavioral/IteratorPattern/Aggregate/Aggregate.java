package com.dzzdsj.design.pattern.demo.behavioral.IteratorPattern.Aggregate;

import com.dzzdsj.design.pattern.demo.behavioral.IteratorPattern.Iterator.Iterator;

/**
 * 定义访问和遍历元素的接口
 */
public interface Aggregate {
    /**
     * 给集合接口定义一个返回迭代器方法 createIterator
     *
     * @return
     */
    Iterator iterator();
}
