package com.dzzdsj.demo.aopdemo;

import org.aopalliance.intercept.Interceptor;
import org.springframework.aop.framework.ProxyFactoryBean;
import org.springframework.aop.support.AopUtils;
import org.springframework.beans.BeansException;
import org.springframework.beans.factory.BeanFactory;
import org.springframework.beans.factory.BeanFactoryAware;
import org.springframework.beans.factory.config.BeanPostProcessor;
import org.springframework.core.PriorityOrdered;
import org.springframework.util.CollectionUtils;

import java.util.Set;

public class MyServiceProcessor implements BeanPostProcessor, BeanFactoryAware, PriorityOrdered {
   BeanFactory beanFactory;
   Set<String> interceptorSet;



    @Override
    public int getOrder() {
        return 0;
    }

    @Override
    public Object postProcessBeforeInitialization(Object bean, String beanName) throws BeansException {
        Class targetClass = AopUtils.getTargetClass(bean);
        System.out.println("enter postProcessBeforeInitialization");
        return bean;
//        if(bean instanceof FactoryBean){
//            try {
//                bean = ((FactoryBean)bean).getObject();
//            } catch (Exception e) {
//                e.printStackTrace();
//            }
//        }
//        return getProxy(bean);
    }

    private Object getProxy(Object bean) {
        ProxyFactoryBean aop = new ProxyFactoryBean();
        aop.setInterfaces(getInterface(bean));
        if(!CollectionUtils.isEmpty(this.interceptorSet)){
            for (String interceptorName: interceptorSet) {
                Interceptor interceptor = (Interceptor) this.beanFactory.getBean(interceptorName);
                aop.addAdvice(interceptor);
            }
        }
        aop.setTarget(bean);
        aop.setBeanFactory(this.beanFactory);
        return aop.getObject();
    }

    private Class<?>[] getInterface(Object bean) {
        Class targetClass = AopUtils.getTargetClass(bean);
        Class<?>[] clazzs = targetClass.getInterfaces();
        if(clazzs != null) {
            return clazzs;
        }
        return new Class[] {bean.getClass()};

    }

    @Override
    public Object postProcessAfterInitialization(Object bean, String beanName) throws BeansException {
        System.out.println("enter postProcessAfterInitialization");
        return bean;
    }

    public BeanFactory getBeanFactory() {
        return beanFactory;
    }

    @Override
    public void setBeanFactory(BeanFactory beanFactory) throws BeansException {
        this.beanFactory = beanFactory;
    }

    public Set<String> getInterceptorSet() {
        return interceptorSet;
    }

    public void setInterceptorSet(Set<String> interceptorSet) {
        this.interceptorSet = interceptorSet;
    }
}
