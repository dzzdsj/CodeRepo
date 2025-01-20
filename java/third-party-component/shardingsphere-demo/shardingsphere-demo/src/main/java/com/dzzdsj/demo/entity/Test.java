package com.dzzdsj.demo.entity;

import lombok.Data;

import javax.persistence.Column;
import javax.persistence.Entity;
import javax.persistence.Id;
import javax.persistence.Table;
import java.io.Serializable;
import java.util.Date;

@Data
@Entity
@Table(name = "t_test")
public class Test implements Serializable {
    private static final long serialVersionUID = 1L;
    @Id
    private Integer id;
    private String name;
    @Column(name = "cust_id")
    private String custId;
    @Column(name="create_time")
    private Date createTime;
    @Column(name="update_time")
    private Date updateTime;
}
