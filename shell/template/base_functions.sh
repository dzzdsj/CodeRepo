init_fifo_queue(){
    #创建有名管道
    if [ -p named_pipe ];then
        rm named_pipe;
        mkfifo -m 644 named_pipe;
    fi
    #将有名管道与文件描述符绑定
    exec 8<>named_pipe;
    #往管道写入数据（主要是靠换行符）,默认5个
    if [ $# -eq 0 ];then
        local size=5;
    else
        local size=$1;
    fi
    local j;
    for j in $(seq 1 $size)
    do
        echo $j;
        echo $j>&8;
    done
}

close_fifo_queue(){
    exec 8<&-
    exec 8>&-
    if [ -p named_pipe ];then
        rm named_pipe;
    fi
}