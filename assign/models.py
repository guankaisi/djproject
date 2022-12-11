import datetime

from django.db import models
from django.utils import timezone

'''
class Student(models.Model):
    STUDENT_TYPES = (
        ('ND', '普通博士'),
        ('DD', '直博'),
        ('SM', '学硕'),
        ('FEM', '全日制工硕'),
        ('PEM', '非全日制工硕')
    )
    id = models.CharField(max_length=11, primary_key=True)
    name = models.CharField(max_length=10)
    stype = models.CharField(max_length=12, choices=STUDENT_TYPES) 
    enroll_date = models.DateField('enrollment date')


class Conduct(models.Model):
    sid = models.OneToOneField(Student, on_delete=models.CASCADE, primary_key=True)
    tid = models.CharField(primary_key=True)
    gid = models.IntegerField()
'''
'''以下是系统初始化时建立的表，省去麻烦直接用sql建表
当删除某个工位时，学生的cid要置空
以后建表的时候要考虑列级，表级，参照完整性约束，明确好违约处理
平衡好表的数量，过多的表确实会承载更多的信息，但是却给查询带来了很多麻烦
当某些表的属性间存在关联时，写好触发器以保持一致性
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
# 删除学生释放工位
DELIMITER |

create trigger release_chair after delete on Student
for each row BEGIN
update Chair C set C.taken = '0' where C.id = old.cid;
END
|
# 添加学生占用工位
DELIMITER |

create trigger take_chair after insert on Student
for each row BEGIN
update Chair C set C.taken = '1' where C.id = new.cid;
END
|
# 改变学生工位，需要把原来工位（如果原来使用工位）置为0，现在工位置为1
create trigger change_chair after update on Student
for each row BEGIN
if old.cid is not NULL then
update Chair C set C.taken = '0' where C.id = OLD.cid;
end if;
update Chair C set C.taken = '1' where C.id = NEW.cid;
END
|
# 删除某个房间，把所有该房间的工位删除
create trigger delete_room before delete on Room
for each row BEGIN
delete from Chair C where C.rid = old.id;
END
|
# 删除工位，原来使用该工位学生不再使用该工位
create delete_chair befor delete on Chair
for each row
# 更新工位代码
先把所有工位的横纵加上20，编号为期望编号
然后把学生使用的工位更新
删除横小于20的工位
把所有工位横纵减20
cursor.execute("select * from Chair")
ch = cursor.fetchall()
for c in ch:
    _row = str(c[2])
    if len(_row)==1:
        _row = '0'+_row
    line = str(c[3])
    if len(line)==1:
        line = '0'+line
    nid = str(c[1])+_row+line
    cursor.execute("insert into Chair values(%s,%s,%s,%s,%s,%s)",[nid, c[1],c[2]+20,c[3]+20,c[4],c[5]])
    cursor.execute("update Student set cid=%s where cid=%s", [nid,c[0]])
cursor.execute("delete from Chair where _row<20")
cursor.execute("update Chair set _row=_row-20, line=line-20)
# 老师和课题组（ganme）为多对一的关系
create table Teacher(
    id char(11) primary key,
    name varchar(10) not null,
    rid integer,
    gname varchar(100),
    last_date date,
    foreign key (rid) references Room(id) // 这一句还未添加到后台数据库
);
# 创建视图，得到每个老师、所在实验室、行、列和他在同一实验室的空闲工位id
create view CTech as
select T.id tid,C.rid rid,C.id cid,C.row row,C.line line
from Chair C,Teacher T
where C.rid = T.rid and C.taken='0'
# 给定一个学生，给学生导师所在实验室的每个工位打分
select C1.cid id, count(*) sco
from CTech C1,CTech C2
where C1.tid='2017202125' and C2.tid='2017202125' and abs(C1.row-C2.row)<=1 and abs(C1.line-C2.line)<=1
group by id
order by sco

# 记录每个用户的username和上次进行学生管理的时间
create table Enroll(
    tid primary key,
    last_date date 
)
#一个学生属于某个老师的某个课题组（存疑）
create table Conduct(
    sid char(11) not null,
    tid char(11) not null,
    gname varchar(100) primary key,
    foreign key(sid) references Student(id),
    foreign key(tid) references Teacher(id),
    unique(sid,tid)
);
#房间
create table Room(
    id integer primary key,
    row integer not null,
    line integer not null
);
#工位，0表示固定工位，1表示临时工位，2表示大门
taken表示一个工位是否被使用，'0'表示未被使用,'1'表示被使用
create table Chair(
    id integer primary key,
    rid integer,
    row integer not null,
    line integer not null,
    ctype enum('0', '1', '2') not null,
    taken enum('0', '1') not null,
    foreign key(rid) references Room(id),
    unique(rid, row, line)
);
create trigger delete_chair after delete on Chair
for each row BEGIN
if 
 
#使用关系（存疑）
create table Occupy(
    sid char(11) primary key,
    rid integer,
    cid integer,
    unique(rid, cid),
    foreign key(sid) references Student(id),
    foreign key(rid) references Room(id),
    foreign key(cid) references Chair(id)
);


insert into Room values(417, 8, 6);
insert into Room values(421, 5, 6);
insert into Teacher values(2017202125, '陈晋川',417,'数据库');
insert into Teacher values(2017202126, '杜小勇', 417, '数据库');
insert into Student values(2018202137, '华思远', '学硕', '2018-1-3', 4170101, '2017202126');
insert into Student values(2018202132, '陈彬', '直博', '2018-1-3',4210101,'2017202125');
#insert into Conduct values(2018202137, 2017202125, 1, '数据库');
#insert into Conduct values(2018202132, 2017202126, 1, '数据科学');
insert into Chair values(4170101, 417, 1, 1, '0','1');
insert into Chair values(4170503, 417, 5, 3, '0','0');
insert into Chair values(4210101, 421, 1, 1, '0','1');

#insert into Occupy values(2018202137, 417, 4170101);
#insert into Occupy values(2018202132, 417, 4170503);
'''