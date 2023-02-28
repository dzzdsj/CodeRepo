package com.dzzdsj.code.ehcachedemo.cache.intercept;

import org.aopalliance.intercept.MethodInterceptor;
import org.aopalliance.intercept.MethodInvocation;
import org.apache.commons.jxpath.JXPathContext;
import org.apache.commons.lang.StringUtils;
import org.springframework.aop.support.AopUtils;
import org.springframework.beans.BeanUtils;
import org.springframework.util.ReflectionUtils;
import java.lang.annotation.Annotation;
import java.lang.reflect.Method;

public abstract class NetbankInterceptor implements MethodInterceptor {

    protected <T extends Annotation> T getTargetAnnotation(MethodInvocation invocation, Class<T> annoClazz) throws Throwable {
        Class<?> clazz = getTargetClassName(invocation);
        Method method = findMethod(clazz, invocation.getMethod().getName(), invocation.getMethod().getParameterTypes());
        T anno = null;
        if (method != null) {
            anno = method.getAnnotation(annoClazz);
        }
        return anno;
    }


    protected static Method findMethod(Class<?> clazz, String name, Class[] paramTypes) {
        return ReflectionUtils.findMethod(clazz, name, paramTypes);
    }

    protected Class<?> getTargetClassName(MethodInvocation invocation) {
        Class<?> clazz = AopUtils.getTargetClass(invocation.getThis());
        return clazz;
    }

    protected static String getFieldsValue(String str, Object object) throws Exception {
        String temp = "";
        if (object != null && isPrototype(object)) {
            temp += object.toString();
        } else {
            if (StringUtils.isEmpty(str)) {
                return "";
            }
            String[] fieldNames = str.split(",");
            for (String name : fieldNames) {
                if (StringUtils.isNotBlank(name)) {
                    name = StringUtils.replace(name, ".", "/");
                    JXPathContext jxPathContext = JXPathContext.newContext(object);
                    temp += jxPathContext.getValue(name);
                }
            }
        }
        return temp;
    }

    protected static boolean isPrototype(Object object) {
        return BeanUtils.isSimpleValueType(object.getClass());
    }

    protected Object findParamentsByClass(Object[] objs, Class<?> clazz) {
        if (objs == null || objs.length == 0) {
            return null;
        }
        for (Object obj : objs) {
            if (clazz.isInstance(obj) || clazz.equals(obj.getClass())) {
                return obj;
            }
        }
        return null;
    }
}