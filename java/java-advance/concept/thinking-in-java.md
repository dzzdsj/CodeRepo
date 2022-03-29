 <div align='center' ><font size='70'>Thinking In Java</font></div>

# 初始化

## 变量的初始化

### 成员变量初始化

- 基础类型初始化为0值
- 布尔类型初始化为false
- 对象的引用初始化为null

```java
Data type      Initial value
boolean        false
char           [ ]        //0
byte           0
short          0
int            0
long           0
float          0.0
double         0.0
reference      null
Integer      null
String      null
```

### 局部变量初始化

- 局部变量未初始化->编译时错误

```
Error:(38, 24) java: 可能尚未初始化变量i
```

### 构造函数初始化

- 可以在构造函数中对成员变量进行初始化，但无法阻止默认的自动初始化

```java
public class Counter {
  int i;
  Counter() { i = 7; }    //i会先置为0，再置为7
  // ...
}
```

## 初始化顺序

- 实例初始化语句将在构造函数之前执行

```java
class Mug {
  Mug(int marker) {
    print("Mug(" + marker + ")");
  }
  void f(int marker) {
    print("f(" + marker + ")");
  }
}

public class Mugs {
  Mug mug1;
  Mug mug2;
  //实例初始化语句将在构造函数之前执行
  {
    mug1 = new Mug(1);
    mug2 = new Mug(2);
    print("mug1 & mug2 initialized");
  }
  Mugs() {
    print("Mugs()");
  }
  Mugs(int i) {
    print("Mugs(int)");
  }
  public static void main(String[] args) {
    print("Inside main()");
    new Mugs();
    print("new Mugs() completed");
    new Mugs(1);
    print("new Mugs(1) completed");
  }
}
```