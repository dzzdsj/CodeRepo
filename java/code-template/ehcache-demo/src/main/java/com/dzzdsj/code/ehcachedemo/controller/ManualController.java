package com.dzzdsj.code.ehcachedemo.controller;


import net.sf.ehcache.CacheManager;
import net.sf.ehcache.Element;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.cache.Cache;
import org.springframework.cache.ehcache.EhCacheCacheManager;
import org.springframework.scheduling.annotation.EnableScheduling;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpSession;
import java.util.concurrent.TimeUnit;

@EnableScheduling
@RestController()
@RequestMapping("/manual")
public class ManualController {
    @Autowired
    private EhCacheCacheManager ehCacheCacheManager;

    @GetMapping("/addCache")
    public void addCache(HttpServletRequest request) {
        HttpSession session = request.getSession();
        String sessionId = session.getId();

        // 确保使用Spring管理的CacheManager和预先配置好的缓存
        Cache cache = ehCacheCacheManager.getCache("localCache"); // 假定你已经在配置中定义了这个名字的缓存

        // 使用session ID作为Element的key，避免覆盖问题
//        Element element = new Element(sessionId, sessionId);

        // 将session ID对应的Element放入缓存
        cache.put(sessionId, sessionId);

        CacheManager cacheManager = CacheManager.getInstance();
        net.sf.ehcache.Cache cache1 = cacheManager.getCache("localCache");
        System.out.println("AllKeys=" + cache1.getKeys());
    }

    @Scheduled(fixedRate = 5000)
    public void refreshCache() {
        CacheManager cacheManager = CacheManager.getInstance();
        net.sf.ehcache.Cache cache1 = cacheManager.getCache("localCache");
        System.out.println("AllKeys=" + cache1.getKeys());
    }

}
