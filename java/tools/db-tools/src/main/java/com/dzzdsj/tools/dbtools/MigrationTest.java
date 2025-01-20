package com.dzzdsj.tools.dbtools;



import oracle.jdbc.OracleConnection;
import org.opengauss.copy.CopyManager;
import org.opengauss.core.BaseConnection;

import java.io.StringReader;
import java.sql.*;
import java.util.Properties;

/**
 *
 */
public class MigrationTest {
    //创建数据库连接。
    public static Connection getOracleConnection() {
        String driver = "oracle.jdbc.driver.OracleDriver";
        String sourceURL = "jdbc:oracle:thin:@dev:1521:dzzdsjdb";
        Connection conn = null;
        try {
//加载数据库驱动。
            Class.forName(driver).newInstance();
        } catch (Exception e) {
            e.printStackTrace();
            return null;
        }
        try {
//创建数据库连接。
            //
//            DriverManager.registerDriver(new oracle.jdbc.driver.OracleDriver());
            Properties props = new Properties();
//            props.put("oracle.net.encryption_client", "accepted");
//            props.put("oracle.net.encryption_client", "rejected");
//            props.put("oracle.net.encryption_types_client", "RC4_256");
            props.put("user", "dzzdsj");
            props.put("password", "dzzdsj");
            conn = DriverManager.getConnection(sourceURL, props);
            OracleConnection oracleConnection = (OracleConnection) conn;
            int result = oracleConnection.pingDatabase();
            System.out.println("result=" + result);
            boolean b = oracleConnection.isValid(0);
            System.out.println("b=" + b);
//            conn = DriverManager.getConnection(sourceURL, username, passwd);
            System.out.println("Connection succeed!");
        } catch (Exception e) {
            e.printStackTrace();
            return null;
        }
        return conn;
    }

    public static Connection getOpenGaussConnection() {
        String driver = "org.opengauss.Driver";
        String sourceURL = "jdbc:opengauss://dev:15400/postgres";
        Connection conn = null;
        try {
            Class.forName(driver).newInstance();
        } catch (Exception e) {
            e.printStackTrace();
            return null;
        }
        try {
//创建数据库连接。
            //
//            DriverManager.registerDriver(new oracle.jdbc.driver.OracleDriver());
            Properties props = new Properties();
//            props.put("oracle.net.encryption_client", "accepted");
//            props.put("oracle.net.encryption_client", "rejected");
//            props.put("oracle.net.encryption_types_client", "RC4_256");
            props.put("user", "dzzdsj");
            props.put("password", "Dzzdsj1991");
            String delimiter = "|";
            String encoding ="UTF8";
            String tableName="dzzdsj.t_test";
            StringBuffer buffer = new StringBuffer();
//            buffer.append("1|test|hfdre     |2024-10-28 23:00:31|2024-10-28 23:00:31");
            buffer.append("1|test|hfdre     |2024-10-28 23:00:31|2024-10-28 23:00:31\n" +
                    "2|\\\\\\\\|vtxlz     |2024-10-28 23:00:31|2024-10-28 23:00:31\n" +
                    "3|\\N|clohp     |2024-10-28 23:00:31|2024-10-28 23:00:31\n" +
                    "4|XRUVA|cccvw     |2024-10-28 23:00:31|2024-10-28 23:00:31");
            conn = DriverManager.getConnection(sourceURL, props);
            BaseConnection baseConn = (BaseConnection) conn;
            baseConn.setAutoCommit(false);
            String sql = "Copy " + tableName + " from STDIN with (DELIMITER " + "'" + delimiter + "'" +"," + "ENCODING " + "'" + encoding + "')";
            CopyManager cp = new CopyManager(baseConn);
            StringReader reader = new StringReader(buffer.toString());
            cp.copyIn(sql, reader);
            baseConn.commit();
            reader.close();
            baseConn.close();
            System.out.println("Connection succeed!");
        } catch (Exception e) {
            e.printStackTrace();
            return null;
        }
        return conn;
    }

    //执行普通SQL语句，创建customer_t1表。
    public static void createTable(Connection conn) {
        Statement stmt = null;
        try {
            stmt = conn.createStatement();
//执行普通SQL语句。
            int rc = stmt
                    .executeUpdate("CREATE TABLE t_student(sid INTEGER, sname VARCHAR(32));");
            stmt.close();
        } catch (SQLException e) {
            if (stmt != null) {
                try {
                    stmt.close();
                } catch (SQLException e1) {
                    e1.printStackTrace();
                }
            }
            e.printStackTrace();
        }
    }

    //执行预处理语句，批量插入数据。
    public static void batchInsertData(Connection conn) {
        PreparedStatement pst = null;
        try {
//生成预处理语句。
            pst = conn.prepareStatement("INSERT INTO t_student VALUES (?,?)");
            for (int i = 0; i < 3; i++) {
//添加参数。
                pst.setInt(1, i);
                pst.setString(2, "data " + i);
                pst.addBatch();
            }
//执行批处理。
            pst.executeBatch();
            pst.close();
        } catch (SQLException e) {
            if (pst != null) {
                try {
                    pst.close();
                } catch (SQLException e1) {
                    e1.printStackTrace();
                }
            }
            e.printStackTrace();
        }
    }

    //执行预编译语句，更新数据。
    public static void execPreparedSQL(Connection conn) {
        PreparedStatement pstmt = null;
        try {
            pstmt = conn
                    .prepareStatement("UPDATE t_student SET sname = ? WHERE sid = 1");
            pstmt.setString(1, "new Data3");
            int rowcount = pstmt.executeUpdate();
            pstmt.close();
        } catch (SQLException e) {
            if (pstmt != null) {
                try {
                    pstmt.close();
                } catch (SQLException e1) {
                    e1.printStackTrace();
                }
            }
            e.printStackTrace();
        }
    }

    //执行预编译语句，更新数据。
    public static void execSelectSQL(Connection conn) {
        PreparedStatement pstmt = null;
        try {
            pstmt = conn
                    .prepareStatement("SELECT sysdate from dual");
            ResultSet resultSet = pstmt.executeQuery();
            while(resultSet.next()){
                System.out.println("+++++++++++++++++++++");
                System.out.println(resultSet.getTime(1));
            }
//            System.out.println(student);
            pstmt.close();
        } catch (SQLException e) {
            if (pstmt != null) {
                try {
                    pstmt.close();
                } catch (SQLException e1) {
                    e1.printStackTrace();
                }
            }
            e.printStackTrace();
        }
    }

    //执行存储过程。
    public static void execCallableSQL(Connection conn) {
        CallableStatement cstmt = null;
        try {
// 存储过程TESTPROC需提前创建。
            cstmt=conn.prepareCall("{? = CALL TESTPROC(?,?,?)}");
            cstmt.setInt(2, 50);
            cstmt.setInt(1, 20);
            cstmt.setInt(3, 90);
            cstmt.registerOutParameter(4, Types.INTEGER); //注册out类型的参数，类型为整型。
            cstmt.execute();
            int out = cstmt.getInt(4); //获取out参数
            System.out.println("The CallableStatment TESTPROC returns:"+out);
            cstmt.close();
        } catch (SQLException e) {
            if (cstmt != null) {
                try {
                    cstmt.close();
                } catch (SQLException e1) {
                    e1.printStackTrace();
                }
            }
            e.printStackTrace();
        }
    }

    /**
     * 主程序，逐步调用各静态方法。
     * @param args
     */
    public static void main(String[] args) {
//创建数据库连接。
//        Connection conn = getConnection("gsdb", "Dzzdsj1991");
        System.out.println(System.currentTimeMillis());
        Connection oracleConn = getOracleConnection();
        Connection openGaussConn = getOpenGaussConnection();
//创建表。
//        createTable(conn);
////批插数据。
//        batchInsertData(conn);
////执行预编译语句，更新数据。
//        execPreparedSQL(conn);
        //执行查询
        System.out.println(System.currentTimeMillis());
        execSelectSQL(oracleConn);
        System.out.println(System.currentTimeMillis());
////执行存储过程。
//        execCallableSQL(conn);
//关闭数据库连接。
        try {
            oracleConn.close();
            openGaussConn.close();
        } catch (SQLException e) {
            e.printStackTrace();
        }
    }
}
