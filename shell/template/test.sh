#!/usr/bin/env bash
foo=a
#单小括号。命令组。括号中的命令将会新开一个子shell顺序执行，所以括号中的变量不能够被脚本余下的部分使用
(
foo=b
echo ${foo} #=>b
)
echo ${foo} #=>a

