drop database if exists mybatisdb;
create database mybatisdb;
use mybatisdb;

drop table if exists user;
create table user(
  id int primary key auto_increment,
  username varchar(20),
  password varchar(20),
  gender varchar(10)
);

insert into user(username,password,gender) values('admin','admin','male');
insert into user(username,password,gender) values('abc','admin','female');
insert into user(username,password,gender) values('cde','admin','female');
insert into user(username,password,gender) values('efg','admin','male');

select * from user;