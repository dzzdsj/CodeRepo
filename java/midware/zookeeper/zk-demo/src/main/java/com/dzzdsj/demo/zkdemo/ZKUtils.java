package com.dzzdsj.demo.zkdemo;

import org.apache.curator.RetryPolicy;
import org.apache.curator.framework.CuratorFramework;
import org.apache.curator.framework.CuratorFrameworkFactory;
import org.apache.curator.framework.recipes.cache.TreeCache;
import org.apache.curator.framework.recipes.cache.TreeCacheListener;
import org.apache.curator.retry.ExponentialBackoffRetry;
import org.apache.zookeeper.CreateMode;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import javax.annotation.PostConstruct;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

@Component
public class ZKUtils {
    private final Logger logger = LoggerFactory.getLogger(this.getClass());
    private CuratorFramework client = null;
    @Value("${zookeeper.server}")
    private String server;
    @Value("${zookeeper.namespace}")
    private String namespace;
    @Value("${zookeeper.digest}")
    private String digest;
    @Value("${zookeeper.sessionTimeoutMs}")
    private Integer sessionTimeoutMs;
    @Value("${zookeeper.connectionTimeoutMs}")
    private Integer connectionTimeoutMs;
    @Value("${zookeeper.maxRetries}")
    private Integer maxRetries;
    @Value("${zookeeper.baseSleepTimeMs}")
    private Integer baseSleepTimeMs;

    @PostConstruct
    public void init() {
        if (client != null) {
            return;
        }
        //重连策略
        RetryPolicy retryPolicy = new ExponentialBackoffRetry(baseSleepTimeMs, maxRetries);
        client = CuratorFrameworkFactory
                .builder()
                .connectString(server)
                .sessionTimeoutMs(sessionTimeoutMs)
                .retryPolicy(retryPolicy)
                .namespace(namespace)
                .build();
        client.start();
    }

    public void createNode(CreateMode mode, String path, String nodeData) {
        try {
            client.create()
                    .creatingParentsIfNeeded()
                    .withMode(mode)
                    .forPath(path, nodeData.getBytes("UTF-8"));
        } catch (Exception e) {
            logger.error("注册出错", e);
        }
    }

    public void createNode(CreateMode mode, String path) {
        try {
            client.create()
                    .creatingParentsIfNeeded()
                    .withMode(mode)
                    .forPath(path);
        } catch (Exception e) {
            logger.error("注册出错", e);
        }
    }

    public byte[] getNodeData(String path) {
        try {
            return client.getData().forPath(path);
        } catch (Exception e) {
            logger.error("{}", e);
        }
        return null;
    }

    ExecutorService pool = Executors.newFixedThreadPool(2);
    public void wathPath(String watchPath, TreeCacheListener listener) {
        TreeCache treeCache = new TreeCache(client, watchPath);
        treeCache.getListenable().addListener(listener, pool);
        try {
            treeCache.start();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }


}
