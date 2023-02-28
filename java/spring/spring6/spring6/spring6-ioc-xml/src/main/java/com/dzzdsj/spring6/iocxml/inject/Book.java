package com.dzzdsj.spring6.iocxml.inject;

public class Book {
    private String bname;
    private String author;

    public Book() {
        System.out.println("无参构造执行了");
    }
    public Book(String bname, String author) {
        System.out.println("有参构造执行了");
        this.bname = bname;
        this.author = author;
    }

    public String getBname() {
        return bname;
    }

    public void setBname(String bname) {
        this.bname = bname;
    }

    public String getAuthor() {
        return author;
    }

    public void setAuthor(String author) {
        this.author = author;
    }

    @Override
    public String toString() {
        return "Book{" +
                "bname='" + bname + '\'' +
                ", author='" + author + '\'' +
                '}';
    }
}
