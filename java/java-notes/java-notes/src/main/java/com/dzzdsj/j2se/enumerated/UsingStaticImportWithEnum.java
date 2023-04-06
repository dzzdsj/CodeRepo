//: enumerated/Burrito.java
package com.dzzdsj.j2se.enumerated;
/**
 * import static 静态引入后，可以直接使用枚举类型的值
 */
import static com.dzzdsj.j2se.enumerated.Spiciness.*;

public class UsingStaticImportWithEnum {
  Spiciness degree;
  public UsingStaticImportWithEnum(Spiciness degree) { this.degree = degree;}
  public String toString() { return "Burrito is "+ degree;}
  public static void main(String[] args) {
    System.out.println(new UsingStaticImportWithEnum(NOT));
    System.out.println(new UsingStaticImportWithEnum(MEDIUM));
    System.out.println(new UsingStaticImportWithEnum(HOT));
  }
} /* Output:
Burrito is NOT
Burrito is MEDIUM
Burrito is HOT
*///:~
