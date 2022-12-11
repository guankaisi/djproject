drop table if exists Student;
create table Student(
    id char(11) primary key,
    name varchar(10) not null,
    stype ENUM('直博', '普通博士', '学硕', '非全日制工硕', '全日制工硕') not null,
    enroll_date date not null,
    cid integer unique,
    tid char(11) not null,
    foreign key(cid) references Chair(id)
    on delete set null,
    foreign key(tid) references Teacher(id)
    on delete cascade
);

drop table if exists Room;
create table Room(
    id integer primary key,
    _row integer not null,
    line integer not null
);


drop table if exists Chair;
create table Chair(
    id integer primary key,
    rid integer,
    _row integer not null,
    line integer not null,
    ctype enum('0', '1', '2') not null,
    taken enum('0', '1') not null,
    foreign key(rid) references Room(id),
    unique(rid, row, line)
);



drop table if exists Teacher;
create table Teacher(
    id char(11) primary key,
    name varchar(10) not null,
    rid integer,
    Title enum('教授','副教授','讲师') not null,
    gname varchar(100),
    last_date date,
    foreign key (rid) references Room(id) // 这一句还未添加到后台数据库
);

drop table if exists Fee;
create table Fee(
    tid char(11) primary key,
    tname varchar(10) not null,
    Title enum('教授','副教授','讲师') not null,
    free_Postgraduate integer check(free_Postgraduate>=0),
    free_Doctor integer check(free_Doctor>=0),
    occupy_Postgraduate integer check(occupy_Postgraduate>=0),
    occupy_Doctor integer check(occupy_Doctor>=0),
    occupy_Other integer check(occupy_Other>=0),
    unit_Price integer check(unit_Price>=0),
    Total_Price integer check(Total_Price>=0),
    pay enum('0','1') not null,
    foreign key(tid) references Teacher(id)
    on delete cascade

);

