package com.dzzdsj.demo.codeutils.DesignPatternRunoobDemo.FilterPattern;

import java.util.ArrayList;
import java.util.List;

//步骤 3
//创建实现了 Criteria 接口的实体类。
public class CriteriaMale implements Criteria {

    @Override
    public List<Person> meetCriteria(List<Person> persons) {
        List<Person> malePersons = new ArrayList<Person>();
        for (Person person : persons) {
            if (person.getGender().equalsIgnoreCase("MALE")) {
                malePersons.add(person);
            }
        }
        return malePersons;
    }
}
