package com.dzzdsj.demo.springdemo.springtest;

import org.junit.Assert;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.context.ContextConfiguration;
import org.springframework.test.context.junit4.SpringJUnit4ClassRunner;

//在Junit环境下提供Spring TestContext Framework的功能
@RunWith(SpringJUnit4ClassRunner.class)
//用来加载配置ApplicationContext, classes属性用来加载配置类
@ContextConfiguration(classes = {TestConfig.class})
//声明活动的profile
@ActiveProfiles("prod")
//@ActiveProfiles("dev")
public class SpringTestDemo {
    @Autowired
    private TestBean testBean;

    @Test
    public void prodBeanInject() {
        String expectedContent = "prod bean";
//        String expectedContent = "dev bean";
        String actualContent = testBean.getContent();
        Assert.assertEquals(expectedContent, actualContent);
    }
}
