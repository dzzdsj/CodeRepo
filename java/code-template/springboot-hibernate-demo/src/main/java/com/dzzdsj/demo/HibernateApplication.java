package com.dzzdsj.demo;


import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.data.jpa.repository.config.EnableJpaAuditing;
import org.springframework.data.jpa.repository.config.EnableJpaRepositories;

/**
 * @author
 * @version 1.0
 */
@SpringBootApplication
@EnableJpaRepositories
@EnableJpaAuditing
public class HibernateApplication {
    private static final Logger logger = LoggerFactory.getLogger(HibernateApplication.class);

    public static void main(String[] args) {
        if (logger.isDebugEnabled()) {
            logger.debug("启动hibernate...");
        }

        SpringApplication.run(HibernateApplication.class, args);
    }

}
