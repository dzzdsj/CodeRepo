package com.dzzdsj.redisdemo;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.web.bind.annotation.GetMapping;

@SpringBootTest
public class RedisTest {
    @Autowired
    private StringRedisTemplate stringRedisTemplate;

    @Autowired
    private RedisTemplate<String, Object> redisTemplate;

    /**
     * StringRedisTemplate默认使用stringSerializer
     */
    @Test
    void stringRedis() {
        String s = "中国人";
        stringRedisTemplate.opsForValue().set("test:string", s);
        String result = stringRedisTemplate.opsForValue().get("test:string");
        System.out.println(result);
    }


    @Test
    void defaultSerialize() {
        RedisTestUser redisTestUser = new RedisTestUser();
        redisTestUser.setId(3L);
        redisTestUser.setName("tom");
        System.out.println(redisTestUser);
        redisTemplate.opsForValue().set("test:defaultSerialize", redisTestUser);
        Object result = redisTemplate.opsForValue().get("test:defaultSerialize");
        System.out.println(result);
    }
}