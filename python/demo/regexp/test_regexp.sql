create database test_regexp;
use test_regexp;
create table t1
(
    a varchar(100),
    b varchar(100)
) engine=innodb default charset=utf8mb4;

 create table t2
(
    c varchar(100),
    d varchar(100),
    primary key(c)
) engine=innodb default charset=utf8mb4 shardkey=c;