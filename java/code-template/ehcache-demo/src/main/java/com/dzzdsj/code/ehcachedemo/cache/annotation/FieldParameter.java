package com.dzzdsj.code.ehcachedemo.cache.annotation;

public @interface FieldParameter {
    int paramIndex();

    String[] fieldName() default {""};
}
