select Student.id,Student.name,stype,Teacher.name,enroll_date,Chair.rid,cid 
from Student Left join Chair on Student.cid=Chair.id,Teacher 
where Student.tid = Teacher.id ;

