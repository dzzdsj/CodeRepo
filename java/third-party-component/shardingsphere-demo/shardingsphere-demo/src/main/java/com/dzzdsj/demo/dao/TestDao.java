package com.dzzdsj.demo.dao;

import com.dzzdsj.demo.entity.Test;
import org.springframework.data.jpa.repository.JpaRepository;

public interface TestDao extends JpaRepository<Test,Integer> {
}
