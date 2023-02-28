package com.dzzdsj.code.databasedemo.jdbc;

import java.sql.*;

public class JDBCDemo {
    public static void main(String[] args) throws Exception {
        String driver = "oracle.jdbc.driver.OracleDriver";
//        String driver = "com.mysql.jdbc.Driver";
        String username = "dzzdsj";
        String password = "dzzdsj";
        String url = "jdbc:oracle:thin:@dev:1521:dzzdsjdb";
//        String url = "jdbc:oracle:thin:@172.20.10.7:1521:dzzdsjdb";
//        String url="jdbc:mysql://localhost:3306/db1?useSSL=false";
        //1.注册驱动
        Class.forName(driver).newInstance();
        //2.获取连接
        Connection conn = DriverManager.getConnection(url, username, password);
        //3.定义sql
        String sql="select sysdate from dual";
        //4.获取执行sql的对象
        PreparedStatement pstmt = null;
        try {
            pstmt = conn.prepareStatement(sql);
            //5.执行sql
            ResultSet resultSet = pstmt.executeQuery();
            //6.处理结果
            while(resultSet.next()){
                System.out.println(resultSet.getTime(1));
            }
            //7.释放资源
            pstmt.close();
            conn.close();
        } catch (SQLException e) {
            if (pstmt != null) {
                try {
                    pstmt.close();
                    conn.close();
                } catch (SQLException e1) {
                    e1.printStackTrace();
                }
            }
            e.printStackTrace();
        }
    }
}
