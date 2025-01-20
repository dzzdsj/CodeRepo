package com.dzzdsj.tools.dbtools;

import io.debezium.engine.ChangeEvent;
import io.debezium.engine.DebeziumEngine;
import io.debezium.engine.format.Json;
import io.debezium.relational.history.FileDatabaseHistory;

import java.util.Properties;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class DebeziumTest {
    public static void main(String[] args) {

        // 1. 生成配置
        Properties props = genProps();

        // 2. 业务处理逻辑部分代码
        DebeziumEngine<ChangeEvent<String, String>> engine = engineBuild(props);

        // 3. 正式运行
        runSoftware(engine);

    }

    private static Properties genProps() {
        // 配置
        Properties props = new Properties();

        props.setProperty("name", "oracle-engine-0033");
        props.setProperty("connector.class", "io.debezium.connector.oracle.OracleConnector");
        props.setProperty("offset.storage", "org.apache.kafka.connect.storage.FileOffsetBackingStore");
        // 指定 offset 存储目录
        props.setProperty("offset.storage.file.filename", "D:\\temp\\oracle4.txt");
        // 指定 Topic offset 写入磁盘的间隔时间
        props.setProperty("offset.flush.interval.ms", "6000");
        //设置数据库连接信息
        props.setProperty("database.hostname", "dev");
        props.setProperty("database.port", "1521");
        props.setProperty("database.user", "dzzdsj");
        props.setProperty("database.password", "dzzdsj");
        props.setProperty("database.server.id", "85701");
        props.setProperty("table.include.list", "dzzdsj.t_tmp");
        props.setProperty("database.history", FileDatabaseHistory.class.getCanonicalName());
        props.setProperty("database.history.file.filename", "D:\\temp\\oracle4.txt");
        //每次运行需要对此参数进行修改，因为此参数唯一
        props.setProperty("database.server.name", "my-oracle-connector-0023");
        //指定 CDB 模式的实例名
        props.setProperty("database.dbname", "dzzdsjdb");
        //是否输出 schema 信息
        props.setProperty("key.converter.schemas.enable", "false");
        props.setProperty("value.converter.schemas.enable", "false");
        props.setProperty("database.serverTimezone", "UTC"); // 时区
        props.setProperty("database.connection.adapter", "logminer"); // 模式
        // Kafka 连接相关配置
        /*props.setProperty("database.history.kafka.bootstrap.servers", "192.168.131.130:9092");
        props.setProperty("database.history.kafka.topic", "oracle.history");*/

        return props;
    }

    // 开始运行程序
    public static void runSoftware(DebeziumEngine<ChangeEvent<String, String>> engine) {
        ExecutorService executor = Executors.newSingleThreadExecutor();
        executor.execute(engine);
    }

    // 实现逻辑
    public static DebeziumEngine<ChangeEvent<String, String>> engineBuild(Properties props) {

        // 2. 构建 DebeziumEngine
        // 使用 Json 格式
        DebeziumEngine<ChangeEvent<String, String>> engine =
                DebeziumEngine
                        .create(Json.class)
                        .using(props)
                        .notifying(record -> {
                            // record中会有操作的类型（增、删、改）和具体的数据
                            System.out.println("record.key() = " + record.key());
                            System.out.println("record.value() = " + record.value());
                        })
                        .using((success, message, error) -> {
                            // 强烈建议加上此部分的回调代码，方便查看错误信息
                            if (!success && error != null) {
                                // 报错回调
                                System.out.println("----------error------");
                                System.out.println(message);
                                //System.out.println(error);
                                error.printStackTrace();
                            }
                        })
                        .build();

        return engine;
    }
}
