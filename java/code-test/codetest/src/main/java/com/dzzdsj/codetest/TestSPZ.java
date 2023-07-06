package com.dzzdsj.codetest;

import java.io.BufferedReader;
import java.io.FileReader;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.Arrays;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class TestSPZ {
    public static void main(String[] args) throws Exception {

//        BufferedReader reader = new BufferedReader(
//                new FileReader("D:/tmp/spz.txt"));
//        String line;
//        while ((line = reader.readLine()) != null) {
//            System.out.println(line);
//        }

        String fileName = "D:/tmp/spz.txt";
        byte[] bytes = Files.readAllBytes(Paths.get(fileName));
        String text = new String(bytes, StandardCharsets.UTF_8);
        System.out.println("===============");
        System.out.println(text);
        System.out.println(Arrays.toString(bytes));

//        byte[] spzBytes = {-28, -74, -82,
//        -23, -66, -96,
//        -23, -66, -95,
//        -23,-66, -94,
//        -23, -66, -93,
//        -23, -66, -92,
//        -23, -66, -91,
//        13,10, 13, 10,
//        57, 70, 65, 48,
//        57, 70, 65, 49,
//        57, 70, 65, 50,
//        57, 70, 65, 51,
//        57, 70, 65, 52,
//        57, 70, 65, 53};
        byte[] spzBytes = {-16, -97, -104, -83};
        String word = new String(spzBytes, StandardCharsets.UTF_8);
        System.out.println("===============");
        System.out.println(word);

        String s = "\uD83D\uDE2D";
        System.out.println(s);
        System.out.println((char) Integer.parseInt("D830",16));

        System.out.println("=================");

        // 要解析的json字符串
        String ss = "\\u67e5\\u8be2\\u6210\\u529f";
        System.out.println(ss); // \u67e5\u8be2\u6210\u529f
        System.out.println(convertUnicodeToCh(ss)); // 查询成功
        System.out.println("---------------");
    }


    /**
     * 将unicode字符串转为正常字符串
     *
     * @param str unicode字符串（比如"\u67e5\u8be2\u6210\u529f"）
     * @return 转换后的字符串（比如"查询成功"）
     */
    private static String convertUnicodeToCh(String str) {
        Pattern pattern = Pattern.compile("(\\\\u(\\w{4}))");
        Matcher matcher = pattern.matcher(str);

        // 迭代，将str中的所有unicode转换为正常字符
        while (matcher.find()) {
            String unicodeFull = matcher.group(1); // 匹配出的每个字的unicode，比如\u67e5
            String unicodeNum = matcher.group(2); // 匹配出每个字的数字，比如\u67e5，会匹配出67e5

            // 将匹配出的数字按照16进制转换为10进制，转换为char类型，就是对应的正常字符了
            char singleChar = (char) Integer.parseInt(unicodeNum, 16);

            // 替换原始字符串中的unicode码
            str = str.replace(unicodeFull, singleChar + "");
        }
        System.out.println("str==" + str);
        return str;
    }
}
