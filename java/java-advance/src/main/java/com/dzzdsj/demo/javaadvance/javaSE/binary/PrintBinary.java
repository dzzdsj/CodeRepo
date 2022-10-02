package com.dzzdsj.demo.javaadvance.javaSE.binary;

/**
 * 打印二进制数的小方法
 */
public class PrintBinary {
    public static void printBinary(byte input) {
        for (int i = 0; i < 8; i++) {
            //每次打印第i位
            int t = (input & 0x80 >>> i) >>> (7 - i);
            System.out.print(t);
        }
        System.out.println("");
    }

    public static void printBinary(short input) {
        for (int i = 0; i < 16; i++) {
            //每次打印第i位
            int t = (input & 0x8000 >>> i) >>> (15 - i);
            System.out.print(t);
        }
        System.out.println("");
    }

    public static void printBinary(int input) {
        for (int i = 0; i < 32; i++) {
            //每次打印第i位
            int t = (input & 0x80000000 >>> i) >>> (31 - i);
            System.out.print(t);
        }
        System.out.println("");
    }

    public static void main(String[] args) {
        byte a = -3;
        short b = -3;
        int c = -3;
        printBinary(a);
        System.out.println(Integer.toBinaryString(a));
        System.out.printf("%x\n",a);
        //按8位十六进制输出，向右靠齐，左边用0补齐
        System.out.printf("十六进制输出"+"%08x\n",a);
        System.out.println(Integer.toHexString(a));
        //按12位八进制输出，向右靠齐，左边用0补齐
        System.out.printf("八进制输出"+"%012o\n",a);
        System.out.println(Integer.toOctalString(a));
        printBinary(b);
        printBinary(c);
        System.out.println("");
    }
}
//11111111111111111111111111111101  (负数以补码形式表示)

/*
 0x80000000是数的十六进制表示，转成二进制表示为10000000000000000000000000000000
 * 运算的优先级，移位运算高于逻辑运算，>>>高于&
 * 位逻辑与运算 1&1 = 1 ，0&1 = 0
 * >>>无符号右移，移出部分舍弃，左边位补0；*/

/*
左移运算符<<

a<<n   将a的二进制数据左移b位，右边移空的部分补0

可以理解为数字a= a*2^n（移了n位）。5<<2 -->5*2^2=20   -5<<2^2=-20

a>>n 将a的二进制数据右移b位，如果最高位是0，则左边移空的部分补0，如果最高位是1，则左边移空的部分补1

可以理解为数字a= a/2^n（移了n位），向下取整。5>>2 ---> 5/2^2=1; -5>>2 --> -5/2^2=-2 (向下取整)

a>>>n  不管最高位是0或1，左边移空部分都补0

正数可以按右移计算，负数没有捷径。
* */