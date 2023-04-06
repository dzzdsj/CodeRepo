package com.dzzdsj.j2se.enumerated;

//: enumerated/SpaceShip.java

/**
 * 重写枚举类的方法
 */
public enum OverridingEnumMethods {
  SCOUT, CARGO, TRANSPORT, CRUISER, BATTLESHIP, MOTHERSHIP;
  //重写方法
  public String toString() {
    String id = name();
    String lower = id.substring(1).toLowerCase();
    return id.charAt(0) + lower;
  }
  public static void main(String[] args) {
    for(OverridingEnumMethods s : values()) {
      System.out.println(s);
    }
  }
} /* Output:
Scout
Cargo
Transport
Cruiser
Battleship
Mothership
*///:~
