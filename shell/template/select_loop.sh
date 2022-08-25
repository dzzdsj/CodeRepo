#!/bin/bash
select dir in /home/oracle /home/dzzdsj quit
do
    if [ ! -z "$dir" ];then
        if [ "$dir" = "quit" ];then
            echo "choose quit"
            break;
        elif [ "$dir" = "/home/oracle" ];then
            echo "choose $dir"
            break
        elif [ "$dir" = "/home/dzzdsj" ];then
            echo "choose $dir"
            break
        else
            echo "choose none"
        fi
    else
        REPLAY="XXXX"
        echo "\$REPLAY=$REPLAY"
    fi
done