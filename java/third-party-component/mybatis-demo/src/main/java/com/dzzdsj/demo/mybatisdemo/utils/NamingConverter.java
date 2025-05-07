package com.dzzdsj.demo.mybatisdemo.utils;

public class NamingConverter {

    /**
     * 将下划线命名的字符串转换为驼峰命名方式。
     * 如果转换前的下划线命名的字符串为空，则返回空字符串。
     * 例如：hello_world -> HelloWorld
     *
     * @param underlineName 下划线命名的字符串
     * @return 驼峰命名的字符串
     */
    public static String underlineToCamel(String underlineName) {
        if (underlineName == null || underlineName.isEmpty()) {
            return underlineName;
        }

        StringBuilder camelNameBuilder = new StringBuilder();
        boolean nextUpperCase = false;

        for (int i = 0; i < underlineName.length(); i++) {
            char currentChar = underlineName.charAt(i);

            if (currentChar == '_') {
                nextUpperCase = true;
            } else {
                if (nextUpperCase) {
                    camelNameBuilder.append(Character.toUpperCase(currentChar));
                    nextUpperCase = false;
                } else {
                    camelNameBuilder.append(Character.toLowerCase(currentChar));
                }
            }
        }

        return camelNameBuilder.toString();
    }

    public static void main(String[] args) {
        System.out.println(underlineToCamel("hello_world"));
    }
}
