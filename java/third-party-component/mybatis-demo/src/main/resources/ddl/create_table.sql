create table t_student(
    sid bigint  primary key auto_increment,
    sname varchar(20),
    age varchar(3),
    card_no varchar(20),
    mobile varchar(11),
    create_time date,
    update_time date
);
create table t_student_map_card_no_sname(
    card_no_sname varchar(30) primary key,
    sid bigint
);
create table t_student_map_mobile(
    mobile varchar(30) primary key,
    sid bigint
);