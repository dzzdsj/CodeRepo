/*
授权声明：
本源码系《Java多线程编程实战指南（核心篇）》一书（ISBN：978-7-121-31065-2，以下称之为“原书”）的配套源码，
欲了解本代码的更多细节，请参考原书。
本代码仅为原书的配套说明之用，并不附带任何承诺（如质量保证和收益）。
以任何形式将本代码之部分或者全部用于营利性用途需经版权人书面同意。
将本代码之部分或者全部用于非营利性用途需要在代码中保留本声明。
任何对本代码的修改需在代码中以注释的形式注明修改人、修改时间以及修改内容。
本代码可以从以下网址下载：
https://github.com/Viscent/javamtia
http://www.broadview.com.cn/31065
*/
package com.dzzdsj.demo.javaadvance.javaSE.multithread.initThread;
import static com.dzzdsj.demo.javaadvance.javaSE.multithread.common.Print.printThreadName;

/**
 * 线程的创建
 */
public class WelcomeApp {
  public static void main(String[] args) {
    // 创建线程
    // 1.定义Thread的子类
    Thread welcomeThread = new WelcomeThread();
    //2.创建runnable接口的实例
    Thread welcomeTask = new Thread(new WelcomeTask());
    //匿名类
    Thread welcomeTask2 = new Thread(new Runnable() {
      @Override
      public void run() {
        printThreadName();
      }
    });

    // 启动线程
    welcomeThread.start();
    welcomeTask.start();
    welcomeTask2.start();
    //直接调用run()方法不会另起线程，仅是当前线程中方法的调用
    welcomeTask2.run();
    // 输出“当前线程”的线程名称
    printThreadName();
  }
}
// 定义Thread类的子类
class WelcomeThread extends Thread {
  // 在该方法中实现线程的任务处理逻辑
  @Override
  public void run() {
    printThreadName();
  }
}

class WelcomeTask implements Runnable {
  // 在该方法中实现线程的任务处理逻辑
  @Override
  public void run() {
    printThreadName();
  }
}