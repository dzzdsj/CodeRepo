package com.dzzdsj.booksourcecode;

import org.apache.zookeeper.WatchedEvent;
import org.apache.zookeeper.Watcher;
import org.apache.zookeeper.ZooKeeper;


public class Master implements Watcher {
    ZooKeeper zk;
    String hostPort;
    Master(String hostPort) {
        this.hostPort = hostPort;
    }
    void startZK() throws Exception{
        zk = new ZooKeeper(hostPort, 15000, this);
    }
    @Override
    public void process(WatchedEvent e) {
        System.out.println(e);
    }
    public static void main(String args[])
            throws Exception {
//        Master m = new Master(args[0]);
        Master m = new Master("192.168.50.99:2181");
        m.startZK();
// wait for a bit
        Thread.sleep(60000);
    }


}
