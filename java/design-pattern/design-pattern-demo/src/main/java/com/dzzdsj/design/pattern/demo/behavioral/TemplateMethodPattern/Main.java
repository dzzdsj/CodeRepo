package com.dzzdsj.design.pattern.demo.behavioral.TemplateMethodPattern;

import com.dzzdsj.design.pattern.demo.behavioral.TemplateMethodPattern.AbstractClass.AbstractDisplay;
import com.dzzdsj.design.pattern.demo.behavioral.TemplateMethodPattern.ConcreteClass.CharDisplay;
import com.dzzdsj.design.pattern.demo.behavioral.TemplateMethodPattern.ConcreteClass.StringDisplay;

/**
 * 模板模式：父类定义执行逻辑、算法和待实现的方法，交给子类来完成（如果算法逻辑修改，只需要修改父类）。
 */
public class Main {
    public static void main(String[] args) {
        AbstractDisplay abstractDisplay1 = new CharDisplay('h');
        AbstractDisplay abstractDisplay2 = new StringDisplay("hello baby");
        abstractDisplay1.display();
        abstractDisplay2.display();
    }
}
