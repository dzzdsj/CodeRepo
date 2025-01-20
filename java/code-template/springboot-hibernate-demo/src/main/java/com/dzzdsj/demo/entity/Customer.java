package com.dzzdsj.demo.entity;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.hibernate.envers.Audited;
import org.springframework.data.annotation.CreatedDate;
import org.springframework.data.annotation.LastModifiedDate;
import org.springframework.data.jpa.domain.support.AuditingEntityListener;

import javax.persistence.*;
import java.io.Serializable;
import java.time.LocalDateTime;

/**
 * @author heyunlin
 * @version 1.0
 */
@Data
@Entity
@Builder
@NoArgsConstructor
@AllArgsConstructor
@Table(name = "t_customer")
@EntityListeners(AuditingEntityListener.class)
public class Customer implements Serializable {
    private static final long serialVersionUID = 18L;

    @Id
    @Audited
    @GeneratedValue(strategy = GenerationType.AUTO)
    private Integer id;

    /**
     * 用户名
     */
    @Column(name = "custname")
    private String custname;

    /**
     * 密码
     */
    @Column(name = "password")
    private String password;

    @CreatedDate
    @Column(name = "create_time")
    private LocalDateTime createTime;

    @LastModifiedDate
    @Audited
    @Column(name = "update_time")
    private LocalDateTime updateTime;
}
