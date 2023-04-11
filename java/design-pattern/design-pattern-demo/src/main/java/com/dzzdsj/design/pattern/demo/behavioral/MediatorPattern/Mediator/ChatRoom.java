package com.dzzdsj.design.pattern.demo.behavioral.MediatorPattern.Mediator;

import com.dzzdsj.design.pattern.demo.behavioral.MediatorPattern.Mediatee.User;

/**
 * 中介者，用于各对象间通讯（各对象通过中介者，而不直接通讯）
 */
public class ChatRoom {
    public static void showMessage(User user, String message) {
        System.out.println(user.getName() + ":" + message);
    }
}
