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

insert Fee values(555,'陈晋川','教授',2,2,3,2,0,100,100,'0');
insert Fee values(666,'杜小勇','教授',2,2,2,2,0,100,0,'1');