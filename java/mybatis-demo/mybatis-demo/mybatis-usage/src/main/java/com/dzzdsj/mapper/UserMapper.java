package com.dzzdsj.mapper;

import com.dzzdsj.pojo.User;
import org.apache.ibatis.annotations.MapKey;

import java.util.List;
import java.util.Map;

public interface UserMapper {
    User selectById(Integer id);
//map封装单行数据
    Map<Integer, User> queryUserMapById(Integer id);
//map封装多行数据
    @MapKey("id")
    Map<Integer, User> queryAllUserMap();
//模糊匹配
    List<User> queryUserByLike(String name);
}
