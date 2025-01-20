package com.dzzdsj.demo.service;


import com.dzzdsj.demo.entity.User;

import java.util.List;

/**
 * @author
 * @version 1.0
 */
public interface UserService {

    /**
     * 查询全部用户
     * @return List<User>
     */
    List<User> selectAll();

    User addOne(User user);

    void updateById(User user,Integer id);
}
