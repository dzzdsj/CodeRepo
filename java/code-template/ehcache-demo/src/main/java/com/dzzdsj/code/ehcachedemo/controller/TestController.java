package com.dzzdsj.code.ehcachedemo.controller;

import net.sf.ehcache.Cache;
import net.sf.ehcache.CacheManager;
import org.springframework.cache.annotation.CacheEvict;
import org.springframework.cache.annotation.Cacheable;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.text.SimpleDateFormat;
import java.util.Date;

@RestController()
@RequestMapping("/test")
public class TestController {

    @Cacheable(value = "localCache", key = "'currentTime'")
    @GetMapping("/currentTime")
    public String currentTime() {
        System.out.println("=====currentTime====");
        SimpleDateFormat simpleDateFormat = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss");
        return simpleDateFormat.format(new Date());
    }

    @Cacheable(value = "localCache", key = "#p0")
    @GetMapping("/p0")
    public String cacheParam0(int p0) {
        SimpleDateFormat simpleDateFormat = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss");
        System.out.println("p0=" + p0 + "," + simpleDateFormat.format(new Date()));
        CacheManager cacheManager = CacheManager.getInstance();
        Cache cache = cacheManager.getCache("localCache");
//        System.out.println("AllKeys=" + cache.getKeys());
        System.out.println("KeysWithExpiryCheck=" + cache.getKeysWithExpiryCheck());
        return String.valueOf(p0);
    }

    @GetMapping("/clear")
    @CacheEvict(value = "localCache", allEntries = true)
    public String clearCache() {
        return "clear";
    }

    @GetMapping("/calculate")
    public String calculateCacheSize() {
        CacheManager cacheManager = CacheManager.getInstance();
        Cache cache = cacheManager.getCache("localCache");
        System.out.println("AllKeys=" + cache.getKeys());
        System.out.println("KeysWithExpiryCheck=" + cache.getKeysWithExpiryCheck());
        System.out.println("InMemorySize=" + cache.calculateInMemorySize());
        System.out.println("OffHeapSize=" + cache.calculateOffHeapSize());
        System.out.println("OnDiskSize=" + cache.calculateOnDiskSize());
        return "calculate";
    }

}
