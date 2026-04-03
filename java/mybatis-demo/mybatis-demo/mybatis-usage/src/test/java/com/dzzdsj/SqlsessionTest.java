package com.dzzdsj;

import com.dzzdsj.mapper.UserMapper;
import com.dzzdsj.pojo.User;
import com.dzzdsj.utils.SqlSessionUtil;
import org.apache.ibatis.session.SqlSession;
import org.junit.Test;

import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.Set;

public class SqlsessionTest {

    @Test
    public void testSelectById() {
        SqlSession sqlSession = null;
        try {
            sqlSession = SqlSessionUtil.getSqlSession();
//使用mapper接口方式
            UserMapper userMapper = sqlSession.getMapper(UserMapper.class);
            int UserId = 1;
            User user = userMapper.selectById(UserId);
            System.out.println(user);
        } catch (Exception e) {
            System.out.println(e);
        } finally {
            SqlSessionUtil.closeSqlSession(sqlSession);
        }
    }

    @Test
    public void testSelectOne() {
        SqlSession sqlSession = null;
        try {
            sqlSession = SqlSessionUtil.getSqlSession();
//          直接使用mapper.xml中的方法，不需使用mapper接口
            String statement = "com.dzzdsj.mapper.UserMapper.selectById";
            int UserId = 1;
            User user = sqlSession.selectOne(statement, UserId);
            System.out.println(user);
        } catch (Exception e) {
            System.out.println(e);
        } finally {
            SqlSessionUtil.closeSqlSession(sqlSession);
        }
    }

    @Test
    public void testSelectAll() {
        SqlSession sqlSession = null;
        try {
            sqlSession = SqlSessionUtil.getSqlSession();
            //          直接使用mapper.xml中的方法，不需使用mapper接口
            String statement = "com.dzzdsj.mapper.UserMapper.selectAll";
            int UserId = 1;
            List<User> list = sqlSession.selectList(statement);
            for (User user : list) {
                System.out.println(user);
            }
        } catch (Exception e) {
            System.out.println(e);
        } finally {
            SqlSessionUtil.closeSqlSession(sqlSession);
        }
    }
}
