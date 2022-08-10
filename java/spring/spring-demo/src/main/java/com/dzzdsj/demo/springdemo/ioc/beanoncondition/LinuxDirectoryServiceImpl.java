package com.dzzdsj.demo.springdemo.ioc.beanoncondition;

public class LinuxDirectoryServiceImpl implements DirectoryService{

    public String showDirectory() {
        return "ls";
    }
}
