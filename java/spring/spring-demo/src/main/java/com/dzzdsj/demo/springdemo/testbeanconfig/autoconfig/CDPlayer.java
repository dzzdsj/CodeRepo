package com.dzzdsj.demo.springdemo.testbeanconfig.autoconfig;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;

/**
 * //@Component注解。这个简单的注解表明该类会作为组件类，并告知Spring要为这个类创建bean
 * 默认装配的bean 是类名的首字母小写，这个例子是 cDPlayer
 * 也可以指定名字 @Component("dd")
 *  Spring支持将@Named作为@Component注解的替代方案。两者之间有一些细微的差异，但是在大多数场景中，它们是可以互相替换
 */
@Component
public class CDPlayer implements MediaPlayer {
  private CompactDisc cd;

  @Autowired
  public CDPlayer(CompactDisc cd) {
    this.cd = cd;
  }

  public void play() {
    cd.play();
  }

}
