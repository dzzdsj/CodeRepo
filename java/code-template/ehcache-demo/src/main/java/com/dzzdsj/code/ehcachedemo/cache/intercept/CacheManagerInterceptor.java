package com.dzzdsj.code.ehcachedemo.cache.intercept;

import net.sf.ehcache.Cache;
import net.sf.ehcache.CacheManager;
import org.aopalliance.intercept.MethodInvocation;
import org.springframework.beans.factory.InitializingBean;

public class CacheManagerInterceptor extends NetbankInterceptor implements InitializingBean {

    private static final String PERS_DICT_CACHE = "PERS_DICT_CACHE";
    private CacheManager cacheManager;

    @Override
    public Object invoke(MethodInvocation invocation) throws Throwable {
        return null;
    }

    @Override
    public void afterPropertiesSet() throws Exception {
        cacheManager = CacheManager.getInstance();
        Cache cache = cacheManager.getCache(PERS_DICT_CACHE);
        if (cache == null) {
            cache = new Cache(PERS_DICT_CACHE, 1000, true, false, 7200, 7200);
            cacheManager.addCache(cache);
        }
    }

//    private Cache getCache() {
//        Cache cache = cacheManager.getCache(PERS_DICT_CACHE);
//
//    }

}
