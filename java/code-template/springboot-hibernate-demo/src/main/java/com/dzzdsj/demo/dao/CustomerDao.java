package com.dzzdsj.demo.dao;
import com.dzzdsj.demo.entity.Customer;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

/**
 * @author
 * @version 1.0
 */
@Repository
public interface CustomerDao extends JpaRepository<Customer, Integer> {

}
