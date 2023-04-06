package com.dzzdsj.springbootcodetemplate;

import com.dzzdsj.springbootcodetemplate.bean.TestBean;
import com.dzzdsj.springbootcodetemplate.bean.XMLBean;
import com.dzzdsj.springbootcodetemplate.util.ApplicationContextUtil;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;

@SpringBootTest
public class ApplicationContextUtilTest {

    @Test
    public void test() {
        TestBean testBean =(TestBean) ApplicationContextUtil.getBean("testBean");
        System.out.println(testBean);
    }
    @Test
    public void testxmlbean() {
        XMLBean xmlBean =(XMLBean) ApplicationContextUtil.getBean("xmlBean");
        System.out.println(xmlBean);
    }
}
