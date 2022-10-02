package com.dzzdsj.demo.javaadvance.javaSE.binary;

/**
 *符号扩展，对于正数来讲，在前面补0； 负数时在前面补1。比如8位的二进制数10000111扩展为16位，我们在前面加上8个1，1111111110000111；如果是正数，则在前面补0。这样进行扩展后，符号和数值的大小都不变
 * 目标类型的长度大于源类型的长度：如果数值类型是有符号的，那么就执行符号扩展；如果是无符号型，如char类型，那么不管它要被转换成什么类型，都执行零扩展（补零）。
 * 目标类型的长度小于源类型的长度：则直接截取目标类型的长度。例如将int型转换成byte型，直接截取int型的右边8位
 */

/**
 基础数据类型占用二进制位数
 有符号型：
 byte = 8
 int = 32
 short = 16
 long = 64
 float = 32
 double = 64
 *boolean 只占一位，用0和1代表false和true。

 无符号型：
 char =  16 */

public class TestBinaryTransform {
    public static void main(String[] args) {
        byte b1 = 3;
        PrintBinary.printBinary(b1);
        byte b2 = -3;
        PrintBinary.printBinary(b2);
        System.out.println(Integer.toBinaryString(b2));
    }
}
