create table t_student(
    sid bigint  primary key auto_increment,
    sname varchar(20),
    age varchar(3),
    card_no varchar(20),
    mobile varchar(11),
    create_time date,
    update_time date
);