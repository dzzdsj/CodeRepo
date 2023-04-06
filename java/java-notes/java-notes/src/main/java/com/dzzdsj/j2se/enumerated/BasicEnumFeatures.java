package com.dzzdsj.j2se.enumerated;
// Capabilities of the Enum class

/**
 * 展示enum的特性和用法
 */
enum Shrubbery { GROUND, CRAWLING, HANGING }

public class BasicEnumFeatures {
  public static void main(String[] args) {
    //遍历
    for(Shrubbery s : Shrubbery.values()) {
      //位置
      System.out.println(s + " ordinal: " + s.ordinal());
      //比较
      System.out.println(s.compareTo(Shrubbery.CRAWLING) + " ");
      System.out.println(s.equals(Shrubbery.CRAWLING) + " ");
      System.out.println(s == Shrubbery.CRAWLING);
      //取类的类型
      System.out.println(s.getDeclaringClass());
      //取枚举名
      System.out.println(s.name());
      System.out.println("----------------------");
    }
    // Produce an enum value from a string name:
    for(String s : "HANGING CRAWLING GROUND".split(" ")) {
      //得到枚举集合
      Shrubbery shrub = Enum.valueOf(Shrubbery.class, s);
      System.out.println(shrub);
    }
  }
} /* Output:
GROUND ordinal: 0
-1
false
false
class com.dzzdsj.j2se.enumerated.Shrubbery
GROUND
----------------------
CRAWLING ordinal: 1
0
true
true
class com.dzzdsj.j2se.enumerated.Shrubbery
CRAWLING
----------------------
HANGING ordinal: 2
1
false
false
class com.dzzdsj.j2se.enumerated.Shrubbery
HANGING
----------------------
HANGING
CRAWLING
GROUND
*///:~
