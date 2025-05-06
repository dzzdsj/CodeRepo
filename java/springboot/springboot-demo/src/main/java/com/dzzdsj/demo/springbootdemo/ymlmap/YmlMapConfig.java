package com.dzzdsj.demo.springbootdemo.ymlmap;

import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.stereotype.Component;

@Component
@ConfigurationProperties(prefix = "yml-map")
public class YmlMapConfig {

}
