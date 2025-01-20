package com.dzzdsj.demo.service;


import com.dzzdsj.demo.entity.Customer;
import java.util.List;

/**
 * @author
 * @version 1.0
 */
public interface CustomerService {

    /**
     * 查询全部用户
     * @return List<User>
     */
    List<Customer> selectAll();

    Customer addOne(Customer customer);
}
