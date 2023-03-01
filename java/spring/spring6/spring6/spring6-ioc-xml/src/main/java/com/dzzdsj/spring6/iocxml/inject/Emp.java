package com.dzzdsj.spring6.iocxml.inject;

import java.util.Arrays;

public class Emp {
    private Dept dept;
    private String ename;
    private Integer age;
    private String[] hobbies;
    public Dept getDept() {
        return dept;
    }

    public String getEname() {
        return ename;
    }

    public Integer getAge() {
        return age;
    }

    public void setDept(Dept dept) {
        this.dept = dept;
    }

    public void setEname(String ename) {
        this.ename = ename;
    }

    public void setAge(Integer age) {
        this.age = age;
    }

    public String[] getHobbies() {
        return hobbies;
    }

    public void setHobbies(String[] hobbies) {
        this.hobbies = hobbies;
    }

    public void work() {
        System.out.println("emp work ....,ename:" + ename + ",age:" + age + ",dept:" + dept);
        dept.info();
    }

    @Override
    public String toString() {
        return "Emp{" +
                "dept=" + dept +
                ", ename='" + ename + '\'' +
                ", age=" + age +
                ", hobbies=" + Arrays.toString(hobbies) +
                '}';
    }
}
