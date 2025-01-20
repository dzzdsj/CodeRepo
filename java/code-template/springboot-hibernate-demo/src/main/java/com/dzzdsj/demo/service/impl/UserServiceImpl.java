package com.dzzdsj.demo.service.impl;
import com.dzzdsj.demo.dao.UserDao;
import com.dzzdsj.demo.entity.User;
import com.dzzdsj.demo.service.UserService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;

/**
 * @author
 * @version 1.0
 */
@Service
public class UserServiceImpl implements UserService {
    private final UserDao userDao;

    @Autowired
    public UserServiceImpl(UserDao userDao) {
        this.userDao = userDao;
    }

    @Override
    public List<User> selectAll() {
        return userDao.findAll();
    }

    @Override
    public User addOne(User user) {
        return userDao.save(user);
    }

    @Override
    public void updateById(User user, Integer id) {
        User dbuser = userDao.findById(id).get();
        dbuser.setUsername(user.getUsername());
        dbuser.setPassword(user.getPassword());
        dbuser.setUpdateTime(user.getUpdateTime());
        userDao.save(dbuser);
    }
}
