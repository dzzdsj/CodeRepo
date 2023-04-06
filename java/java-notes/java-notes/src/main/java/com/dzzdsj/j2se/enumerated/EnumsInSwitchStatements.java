package com.dzzdsj.j2se.enumerated;//: enumerated/TrafficLight.java
// Enums in switch statements.
// Define an enum type:

/**
 * enums in switch statements
 */
enum Signal { GREEN, YELLOW, RED, }

public class EnumsInSwitchStatements {
  Signal color = Signal.RED;
  public void change() {
    switch(color) {
      // Note that you don't have to say Signal.RED
      // in the case statement:
      case RED:    color = Signal.GREEN;
                   break;
      case GREEN:  color = Signal.YELLOW;
                   break;
      case YELLOW: color = Signal.RED;
                   break;
    }
  }
  public String toString() {
    return "The traffic light is " + color;
  }
  public static void main(String[] args) {
    EnumsInSwitchStatements t = new EnumsInSwitchStatements();
    for(int i = 0; i < 7; i++) {
      System.out.println(t);
      t.change();
    }
  }
} /* Output:
The traffic light is RED
The traffic light is GREEN
The traffic light is YELLOW
The traffic light is RED
The traffic light is GREEN
The traffic light is YELLOW
The traffic light is RED
*///:~
