package com.dzzdsj.demo.springdemo.testbeanconfig.javaconfig;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class CDPlayerConfig {
  /**
   *@Bean注解会告诉Spring这个方法将会返回一个对象，该对象要注册
   * 为Spring应用上下文中的bean。方法体中包含了最终产生bean实例的逻辑
   * Spring将会拦截所有对它的调用，并确保直接返回该方法所创建的
   * bean，而不是每次都对其进行实际的调用
   * 。默认情况下，Spring中的bean都是单例的
   */
  @Bean
  public CompactDisc compactDisc() {
    return new SgtPeppers();
  }
  
  @Bean
  public CDPlayer cdPlayer(CompactDisc compactDisc) {
    return new CDPlayer(compactDisc);
  }

}
