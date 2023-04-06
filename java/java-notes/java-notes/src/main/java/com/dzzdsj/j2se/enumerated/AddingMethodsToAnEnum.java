package com.dzzdsj.j2se.enumerated;//: enumerated/OzWitch.java
// The witches in the land of Oz.

/**
 * 为枚举对象添加方法
 */
public enum AddingMethodsToAnEnum {
  // Instances must be defined first, before methods:
  WEST("Miss Gulch, aka the Wicked Witch of the West"),
  NORTH("Glinda, the Good Witch of the North"),
  EAST("Wicked Witch of the East, wearer of the Ruby " +
    "Slippers, crushed by Dorothy's house"),
  SOUTH("Good by inference, but missing");//注意这里的分号
  private String description;
  // Constructor must be package or private access:
  private AddingMethodsToAnEnum(String description) {
    this.description = description;
  }
  public String getDescription() { return description; }
  public static void main(String[] args) {
    for(AddingMethodsToAnEnum witch : AddingMethodsToAnEnum.values())
      System.out.println(witch + ": " + witch.getDescription());
  }
} /* Output:
WEST: Miss Gulch, aka the Wicked Witch of the West
NORTH: Glinda, the Good Witch of the North
EAST: Wicked Witch of the East, wearer of the Ruby Slippers, crushed by Dorothy's house
SOUTH: Good by inference, but missing
*///:~
