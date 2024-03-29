///*
//授权声明：
//本源码系《Java多线程编程实战指南（核心篇）》一书（ISBN：978-7-121-31065-2，以下称之为“原书”）的配套源码，
//欲了解本代码的更多细节，请参考原书。
//本代码仅为原书的配套说明之用，并不附带任何承诺（如质量保证和收益）。
//以任何形式将本代码之部分或者全部用于营利性用途需经版权人书面同意。
//将本代码之部分或者全部用于非营利性用途需要在代码中保留本声明。
//任何对本代码的修改需在代码中以注释的形式注明修改人、修改时间以及修改内容。
//本代码可以从以下网址下载：
//https://github.com/Viscent/javamtia
//http://www.broadview.com.cn/31065
//*/
//package com.dzzdsj.demo.codeutils.JavaSE.Thread.MultiThreadInAction.ch2;
//
//import io.github.viscent.mtia.util.Tools;
//
//public class VisibilityDemo {
//
//  public static void main(String[] args) throws InterruptedException {
//    TimeConsumingTask timeConsumingTask = new TimeConsumingTask();
//    Thread thread = new Thread(new TimeConsumingTask());
//    thread.start();
//
//    // 指定的时间内任务没有执行结束的话，就将其取消
//    Thread.sleep(10000);
//    timeConsumingTask.cancel();
//  }
//}
//
//class TimeConsumingTask implements Runnable {
//  private boolean toCancel = false;
//
//  @Override
//  public void run() {
//    while (!toCancel) {
//      if (doExecute()) {
//        break;
//      }
//    }
//    if (toCancel) {
//      System.out.println("Task was canceled.");
//    } else {
//      System.out.println("Task done.");
//    }
//  }
//
//  private boolean doExecute() {
//    boolean isDone = false;
//    System.out.println("executing...");
//
//    // 模拟实际操作的时间消耗
//    Tools.randomPause(50);
//    // 省略其他代码
//
//    return isDone;
//  }
//
//  public void cancel() {
//    toCancel = true;
//    System.out.println(this + " canceled.");
//  }
//}