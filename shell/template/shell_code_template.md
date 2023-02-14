## 循环

### for循环

#### for in 

```shell
for i in {1..3}
do
  echo ${i};
done

for i in {5..1}
do
  echo ${i};
done
```



## 常用命令

### shell合并多行

```shell
#使用paste命令格式化打印，-d指定分隔符，-s表示合并成一行：
paste -d " " -s < test.txt

#使用awk将多行合并为以逗号分隔的1行，去掉%后面的逗号，则直接合并，这种方法需要使用echo补充换行，否则wc -l 等命令将识别为0行
awk  '{{printf"%s,",$0}}'

#sed可以将其他符号替换为换行，但不能把换行替换为其他
sed 's/,/\n/g'     ok
sed 's/\n/,/g'     fail
```

### shell 读取文件指定单行 多行 连续行 倒数几行

```shell
#tail -n -数字 文件名，表示查看文件的最后几行
tail -n -5 SpecialVariable.sh
#tail -n +数字 文件名，表示查看文件的某一行到最后一行
tail -n +3 SpecialVariable.sh
#head -n 数字 文件名，表示查看文件前几行的内容
head -n 3 SpecialVariable.sh
#读取文件列表倒数2行
ls /data/mysql/log/binlog |head -n -2
#sed -n "开始行，结束行p" 文件名，表示查看文件的开始行到结束行的内容，
sed -n "5,9p" SpecialVariable.sh
#打印1~5行与第9行.
sed -n '1,5p;9p' test.txt
```

