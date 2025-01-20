package com.dzzdsj.demo.controller;

import com.dzzdsj.demo.entity.Customer;
import com.dzzdsj.demo.entity.User;
import com.dzzdsj.demo.service.CustomerService;
import com.dzzdsj.demo.service.UserService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RequestMapping("customer")
@RestController
public class CustomerController {
    @Autowired
    private CustomerService customerService;

    @GetMapping("selectAll")
    public List<Customer> selectAll(){
        List<Customer> customerList = customerService.selectAll();
        return customerList;
    }

    @PostMapping("addOne")
    public Customer addOne(@RequestBody Customer customer){
        return   customerService.addOne(customer);
    }
}
