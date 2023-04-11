package com.dzzdsj.design.pattern.demo.behavioral.MediatorPattern.Mediatee;

import com.dzzdsj.design.pattern.demo.behavioral.MediatorPattern.Mediator.ChatRoom;

public class User {
    private String name;

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }


    public User(String name) {
        this.name = name;
    }

    public void showMessage(String massage) {
        ChatRoom.showMessage(this, massage);
    }
}
