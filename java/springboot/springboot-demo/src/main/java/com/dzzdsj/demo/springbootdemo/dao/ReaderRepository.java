package com.dzzdsj.demo.springbootdemo.dao;

import com.dzzdsj.demo.springbootdemo.entity.Reader;
import org.springframework.data.jpa.repository.JpaRepository;

public interface ReaderRepository extends JpaRepository<Reader,Long> {

}
