package com.dzzdsj;

import com.dzzdsj.mapper.UserMapper;
import com.dzzdsj.pojo.User;
import org.apache.ibatis.io.Resources;
import org.apache.ibatis.session.SqlSession;
import org.apache.ibatis.session.SqlSessionFactory;
import org.apache.ibatis.session.SqlSessionFactoryBuilder;
import org.junit.Test;

import java.io.InputStream;

public class MybatisTest {
    @Test
    public void testSelectById(){
        SqlSession sqlSession = null;
        try{
            String fileName = "mybatis-config.xml";
            InputStream inputStream = Resources.getResourceAsStream(fileName);
            SqlSessionFactoryBuilder sqlSessionFactoryBuilder = new SqlSessionFactoryBuilder();
            SqlSessionFactory sqlSessionFactory = sqlSessionFactoryBuilder.build(inputStream);
            sqlSession = sqlSessionFactory.openSession(true);
            UserMapper userMapper = sqlSession.getMapper(UserMapper.class);
            int userId = 1;
            User user = userMapper.selectById(userId);
            System.out.println(user);
        }catch (Exception e){
            System.out.println(e);
        }finally {
            if(sqlSession != null){
                sqlSession.close();
            }
        }
    }
}
