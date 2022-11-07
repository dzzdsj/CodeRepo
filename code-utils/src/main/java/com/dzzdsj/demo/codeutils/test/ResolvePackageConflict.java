package com.dzzdsj.demo.codeutils.test;

/**
 * 容器和应用包冲突时排查方法：
 * 使用反射获取加载到的包，打印其路径，确定程序运行时使用到的包是哪个
 */
public class ResolvePackageConflict {
    public static void main(String[] args) {
        //test
        Class<?> c = null;
        try {
            c = Class.forName("oracle.jdbc.driver.OracleDriver");
        } catch (ClassNotFoundException e) {
            e.printStackTrace();
        }

        System.out.println(c.getProtectionDomain().getCodeSource().getLocation());
    }
}
