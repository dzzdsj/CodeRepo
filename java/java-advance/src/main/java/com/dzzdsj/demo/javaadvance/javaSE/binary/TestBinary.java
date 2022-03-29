package com.dzzdsj.demo.javaadvance.javaSE.binary;

public class TestBinary {
    public static void main(String[] args) {
        int a = 0b11;
        System.out.println("a="+a);
        int b = 0x11;
        System.out.println("b="+b);
        int c = 011;
        System.out.println("c="+c);
        int d = 0xff;
        System.out.println("d="+d);
        int e = 0x0ff;
        System.out.println("e="+e);

        byte[] bytes = new byte[2];
        bytes[1] = 0b0000101;
        System.out.println("g:"+ (bytes[1] & 0x0ff));
        System.out.println("-------------------------------");
        int size = 8191;
        int length = size + 2;
        byte[] buffer = new byte[2];
        buffer[0] = (byte) ((length >> 8) & 0x0ff);

        buffer[1] = (byte) ((length) & 0x0ff);
        System.out.println("buffer0=" + buffer[0]);
        System.out.println("buffer1=" + buffer[1]);

        System.out.println("------------------------------");
        int length2 = 0;
        length2 |= (((int) buffer[1]) & 0x0ff);
        System.out.println("length2="+length2);
        length2 |= (((int) buffer[0]) & 0x0ff) << 8;
        buffer[0] = (byte) ((length >> 8) & 0x0ff);
        buffer[1] = (byte) ((length) & 0x0ff);
        System.out.println("buffer0=" + buffer[0]);
        System.out.println("buffer1=" + buffer[1]);
        System.out.println("length2="+length2);
    }
}
