package org.example;

public class DiffInfo {
    private String shortAcct;
    private String shortAmount;
    private String longAcct;
    private String longAmount;

    public String getShortAcct() {
        return shortAcct;
    }

    public void setShortAcct(String shortAcct) {
        this.shortAcct = shortAcct;
    }

    public String getShortAmount() {
        return shortAmount;
    }

    public void setShortAmount(String shortAmount) {
        this.shortAmount = shortAmount;
    }

    public String getLongAcct() {
        return longAcct;
    }

    public void setLongAcct(String longAcct) {
        this.longAcct = longAcct;
    }

    public String getLongAmount() {
        return longAmount;
    }

    public void setLongAmount(String longAmount) {
        this.longAmount = longAmount;
    }

    @Override
    public String toString() {
        return "DiffInfo{" +
                "shortAcct='" + shortAcct + '\'' +
                ", shortAmount='" + shortAmount + '\'' +
                ", longAcct='" + longAcct + '\'' +
                ", longAmount='" + longAmount + '\'' +
                '}';
    }
}
