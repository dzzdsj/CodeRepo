package com.dzzdsj.demo.service.impl;

import com.dzzdsj.demo.dao.CustomerDao;
import com.dzzdsj.demo.entity.Customer;
import com.dzzdsj.demo.service.CustomerService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;

/**
 * @author
 * @version 1.0
 */
@Service
public class CustomerServiceImpl implements CustomerService {
    private final CustomerDao customerDao;

    @Autowired
    public CustomerServiceImpl(CustomerDao customerDao) {
        this.customerDao = customerDao;
    }

    @Override
    public List<Customer> selectAll() {
        return customerDao.findAll();
    }

    @Override
    public Customer addOne(Customer customer) {
        return customerDao.save(customer);
    }
}
