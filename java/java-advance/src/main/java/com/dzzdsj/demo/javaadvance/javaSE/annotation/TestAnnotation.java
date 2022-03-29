package com.dzzdsj.demo.javaadvance.javaSE.annotation;

/**
 * 使用反射 判断是否有对应的注解 ，获取注解信息的值
 */
public class TestAnnotation {
    public static void main(String[] args) {
        try {
            Class clazz = Class.forName("com.dzzdsj.demo.javaadvance.javaSE.annotation.WithAnnotation");
//            Class clazz = Class.forName("com.dzzdsj.demo.javaadvance.javaSE.annotation.Test");
            //该元素上是否配置有某个指定的注解
            if(clazz.isAnnotationPresent(MyAnnotation.class)){
                //获取注解，方法上的注解要用Method对象获取,属性用Field，类用Class
                MyAnnotation myAnnotation = (MyAnnotation) clazz.getAnnotation(MyAnnotation.class);
                //获取所有注解类型
//                Annotation[] annotations = clazz.getAnnotations();
                System.out.println("name="+myAnnotation.name());
                System.out.println("age="+myAnnotation.age());
                StringBuilder sb = new StringBuilder();
                for(int i:myAnnotation.score()){
                    sb.append(i);
                    sb.append(",");
                }
                System.out.println("score="+ sb);
            }else {
                System.out.println("no annotation");
            }
        } catch (ClassNotFoundException e) {
            e.printStackTrace();
        }
    }
}
