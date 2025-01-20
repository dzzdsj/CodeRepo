package com.dzzdsj.demo.controller;

import com.dzzdsj.demo.entity.User;
import com.dzzdsj.demo.service.UserService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RequestMapping("user")
@RestController
public class UserController {
    @Autowired
    private UserService userService;

    @GetMapping("selectAll")
    public List<User> selectAll(){
        List<User> userList = userService.selectAll();
        return userList;
    }

    @PostMapping("addOne")
    public User addOne(@RequestBody User user){
        return   userService.addOne(user);
    }

    @PostMapping("updateById")
    public void updateById(@RequestBody User user){
           userService.updateById(user,user.getId());
    }
}
