package com.dzzdsj.demo.zkdemo;

import org.apache.curator.framework.CuratorFramework;
import org.apache.curator.framework.recipes.cache.TreeCacheEvent;
import org.apache.curator.framework.recipes.cache.TreeCacheListener;
import org.apache.zookeeper.CreateMode;
import org.junit.jupiter.api.Test;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;

import java.io.UnsupportedEncodingException;

@SpringBootTest
public class TestZKUtils {
    @Autowired
    ZKUtils zkUtils;

    private final Logger logger = LoggerFactory.getLogger(this.getClass());

    @Test
    public void test(){
        zkUtils.createNode(CreateMode.PERSISTENT, "/test", "testData");
        byte[] bytes = zkUtils.getNodeData("/test");
        try {
            String data = new String(bytes,"UTF-8");
            logger.info("data={}",data);
        } catch (UnsupportedEncodingException e) {
            e.printStackTrace();
        }
        zkUtils.wathPath("/test", new TreeCacheListener() {
            @Override
            public void childEvent(CuratorFramework curatorFramework, TreeCacheEvent treeCacheEvent) throws Exception {
                logger.info(treeCacheEvent.getType() + ":" + treeCacheEvent.getData() );
            }
        });
    }
}
