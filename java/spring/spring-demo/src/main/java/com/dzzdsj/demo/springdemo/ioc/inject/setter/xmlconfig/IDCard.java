package com.dzzdsj.demo.springdemo.ioc.inject.setter.xmlconfig;

import lombok.Data;

@Data
public class IDCard {
    int cardNumber;
    int isValid;

    public int getCardNumber() {
        return cardNumber;
    }

    public void setCardNumber(int cardNumber) {
        this.cardNumber = cardNumber;
    }

    public int getIsValid() {
        return isValid;
    }

    public void setIsValid(int isValid) {
        this.isValid = isValid;
    }
}
