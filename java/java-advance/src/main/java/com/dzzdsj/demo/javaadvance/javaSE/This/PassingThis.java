package com.dzzdsj.demo.javaadvance.javaSE.This;//: initialization/PassingThis.java
/**
 * 方法的调用者和入参正好是同一个对象时，使用this进行传递
 */
class Person {
  public void eat(Apple apple) {
    Apple peeled = apple.getPeeled();
    System.out.println("Yummy");
  }
}

/**
 * 剥皮
 */
class Peeler {
  static Apple peel(Apple apple) {
    // ... remove peel
    return apple; // Peeled
  }
}

/**
 * 方法的调用者和入参正好是同一个对象.
 * 这里是个无参方法，但是使用this关键字巧妙的将自己的调用者的引用继续向下传递
 */
class Apple {
  Apple getPeeled() { return Peeler.peel(this); }
}

public class PassingThis {
  public static void main(String[] args) {
    new Person().eat(new Apple());
  }
} /* Output:
Yummy
*///:~
