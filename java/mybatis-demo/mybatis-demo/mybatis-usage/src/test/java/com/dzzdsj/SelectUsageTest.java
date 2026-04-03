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

public class SelectUsageTest {
    @Test
    public void testQueryUserMapById() {
        SqlSession sqlSession = null;
        try {
            sqlSession = SqlSessionUtil.getSqlSession();
            UserMapper userMapper = sqlSession.getMapper(UserMapper.class);
            int userId = 1;
            Map<Integer, User> userMap = userMapper.queryUserMapById(userId);
            Set<Integer> keySet = userMap.keySet();
            Iterator<Integer> iterator = keySet.iterator();
            while(iterator.hasNext()){
                int key = iterator.next();
                System.out.println(userMap.get(key));
            }
        } catch (Exception e) {
            System.out.println(e);
        } finally {
            SqlSessionUtil.closeSqlSession(sqlSession);
        }
    }

    @Test
    public void testQueryAllUser() {
        SqlSession sqlSession = null;
        try {
            sqlSession = SqlSessionUtil.getSqlSession();
            UserMapper userMapper = sqlSession.getMapper(UserMapper.class);
            Map<Integer, User> userMap = userMapper.queryAllUserMap();
            Set<Integer> keySet = userMap.keySet();
            Iterator<Integer> iterator = keySet.iterator();
            while(iterator.hasNext()){
                int key = iterator.next();
                System.out.println(userMap.get(key));
            }
        } catch (Exception e) {
            System.out.println(e);
        } finally {
            SqlSessionUtil.closeSqlSession(sqlSession);
        }
    }
    @Test
    public void testQueryUserByLike(){
        SqlSession sqlSession = null;
        try {
            sqlSession = SqlSessionUtil.getSqlSession();
            UserMapper userMapper = sqlSession.getMapper(UserMapper.class);
            List< User> userList = userMapper.queryUserByLike("dzz");
            System.out.println(userList);
        } catch (Exception e) {
            System.out.println(e);
        }
    }
}
