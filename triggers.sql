drop trigger if exists delete_chair;
CREATE Trigger delete_chair
BEFORE DELETE on Student
FOR EACH ROW
BEGIN
  update Chair C set C.taken = '0' where C.id = new.id;
END;



drop trigger if exists delete_room;
CREATE Trigger delete_room 
BEFORE DELETE on Room
FOR EACH ROW
BEGIN 
  delete from Chair C where C.rid = old.id; 
END;



drop trigger if exists take_chair;
CREATE Trigger take_chair
AFTER INSERT on Student
FOR EACH ROW
BEGIN 
  update Chair C set C.taken = '1' where C.id = new.cid; 
END;

drop trigger if exists change_chair;
CREATE Trigger change_chair 
AFTER UPDATE on Student
FOR EACH ROW
BEGIN 
  if old.cid is not NULL then update Chair C set C.taken = '0' where C.id = OLD.cid; end if; update Chair C set C.taken = '1' where C.id = NEW.cid; 
END;

drop trigger if exists release_chair
CREATE Trigger release_chair
AFTER DELETE on Student
FOR EACH ROW
BEGIN 
  update Chair C set C.taken='0' where C.id = old.cid; 
END;


drop trigger if exists insert_teacher;
CREATE Trigger insert_teacher
AFTER INSERT on Teacher
FOR EACH ROW
BEGIN IF (new.title = '教授') THEN INSERT INTO Fee VALUES (new.id, new.name, new.title, 2, 2, 0, 0, 0, 100, 0, '0'); END IF; IF (new.title = '副教授') THEN INSERT INTO Fee VALUES (new.id, new.name, new.title, 2, 1, 0, 0, 0, 100, 0, '0'); END IF; IF (new.title = '讲师') Then INSERT INTO Fee VALUES (new.id, new.name, new.title, 2, 0, 0, 0, 0, 100, 0, '0'); END IF; 
END;


drop trigger if exists  insert_student;
CREATE Trigger insert_student
AFTER INSERT on Student
FOR EACH ROW
BEGIN
  IF (new.stype in ('直博', '普通博士') AND new.cid IS NOT NULL)
    Then IF EXISTS(SELECT * from Fee where Fee.tid = new.tid and Fee.occupy_Doctor + 1 > Fee.free_Doctor)
          Then UPDATE Fee SET Fee.occupy_Doctor = Fee.occupy_Doctor + 1, Fee.Total_Price = Fee.Total_Price + 4*Fee.unit_Price
                WHERE Fee.tid = new.tid;
        ELSE
            UPDATE Fee SET Fee.occupy_Doctor = Fee.occupy_Doctor + 1
            WHERE Fee.tid = new.tid;
        END IF;
  END IF;
  IF (new.stype = '学硕' AND new.cid IS NOT NULL)
    Then IF EXISTS(SELECT * from Fee where Fee.tid = new.tid and Fee.occupy_Postgraduate + 1 > Fee.free_Postgraduate)
          Then UPDATE Fee SET Fee.occupy_Postgraduate = Fee.occupy_Postgraduate + 1, Fee.Total_Price = Fee.Total_Price + 4*Fee.unit_Price
                WHERE Fee.tid = new.tid;
        ELSE
            UPDATE Fee SET Fee.occupy_Postgraduate = Fee.occupy_Postgraduate + 1
            WHERE Fee.tid = new.tid;
        END IF;
  END IF;
  IF (new.stype in ('非全日制工硕', '全日制工硕')  AND new.cid IS NOT NULL)
    Then  UPDATE Fee SET Fee.occupy_Other = Fee.occupy_Other + 1, Fee.Total_Price = Fee.Total_Price + 4*Fee.unit_Price
          WHERE Fee.tid = new.tid;
  END IF;
END;


drop trigger if exists delete_student;
CREATE Trigger delete_student
BEFORE DELETE on Student
FOR EACH ROW
BEGIN
  IF (old.stype in ('直博', '普通博士') AND old.cid IS NOT NULL)
    Then IF EXISTS(SELECT * from Fee where Fee.tid = old.tid and Fee.occupy_Doctor - 1 >= Fee.free_Doctor)
           Then UPDATE Fee SET Fee.occupy_Doctor = Fee.occupy_Doctor - 1, Fee.Total_Price = Fee.Total_Price - 4*Fee.unit_Price
                WHERE Fee.tid = old.tid;
         ELSE
            UPDATE Fee SET Fee.occupy_Doctor = Fee.occupy_Doctor - 1
            WHERE Fee.tid = old.tid;
         END IF;
  END IF;
  IF (old.stype = '学硕' AND old.cid IS NOT NULL)
    Then IF EXISTS(SELECT * from Fee where Fee.tid = old.tid and Fee.occupy_Postgraduate - 1 >= Fee.free_Postgraduate)
           Then UPDATE Fee SET Fee.occupy_Postgraduate = Fee.occupy_Postgraduate - 1, Fee.Total_Price = Fee.Total_Price - 4*Fee.unit_Price
                WHERE Fee.tid = old.tid;
         ELSE
            UPDATE Fee SET Fee.occupy_Postgraduate = Fee.occupy_Postgraduate - 1
            WHERE Fee.tid = old.tid;
         END IF;
  END IF;
  IF (old.stype in ('非全日制工硕', '全日制工硕')  AND old.cid IS NOT NULL)
    Then  UPDATE Fee SET Fee.occupy_Other = Fee.occupy_Other - 1, Fee.Total_Price = Fee.Total_Price - 4*Fee.unit_Price
          WHERE Fee.tid = old.tid;
  END IF;
END;


drop trigger if exists update_student;
CREATE Trigger update_student
BEFORE UPDATE ON Student
For Each Row
BEGIN
  IF (new.stype in ('直博', '普通博士') AND new.cid IS NOT NULL AND old.cid IS NULL)
    Then IF EXISTS(SELECT * from Fee where Fee.tid = new.tid and Fee.occupy_Doctor + 1 > Fee.free_Doctor)
          Then UPDATE Fee SET Fee.occupy_Doctor = Fee.occupy_Doctor + 1, Fee.Total_Price = Fee.Total_Price + 4*Fee.unit_Price
                WHERE Fee.tid = new.tid;
        ELSE
            UPDATE Fee SET Fee.occupy_Doctor = Fee.occupy_Doctor + 1
            WHERE Fee.tid = new.tid;
        END IF;
  END IF;
  IF (new.stype = '学硕' AND new.cid IS NOT NULL AND old.cid IS NULL)
    Then IF EXISTS(SELECT * from Fee where Fee.tid = new.tid and Fee.occupy_Postgraduate + 1 > Fee.free_Postgraduate)
          Then UPDATE Fee SET Fee.occupy_Postgraduate = Fee.occupy_Postgraduate + 1, Fee.Total_Price = Fee.Total_Price + 4*Fee.unit_Price
                WHERE Fee.tid = new.tid;
        ELSE
            UPDATE Fee SET Fee.occupy_Postgraduate = Fee.occupy_Postgraduate + 1
            WHERE Fee.tid = new.tid;
        END IF;
  END IF;
  IF (new.stype in ('非全日制工硕', '全日制工硕')  AND new.cid IS NOT NULL AND old.cid IS NULL)
    Then  UPDATE Fee SET Fee.occupy_Other = Fee.occupy_Other + 1, Fee.Total_Price = Fee.Total_Price + 4*Fee.unit_Price
          WHERE Fee.tid = new.tid;
  END IF;
  IF (old.stype in ('直博', '普通博士') AND old.cid IS NOT NULL AND new.cid IS NULL)
    Then IF EXISTS(SELECT * from Fee where Fee.tid = old.tid and Fee.occupy_Doctor - 1 >= Fee.free_Doctor)
           Then UPDATE Fee SET Fee.occupy_Doctor = Fee.occupy_Doctor - 1, Fee.Total_Price = Fee.Total_Price - 4*Fee.unit_Price
                WHERE Fee.tid = old.tid;
         ELSE
            UPDATE Fee SET Fee.occupy_Doctor = Fee.occupy_Doctor - 1
            WHERE Fee.tid = old.tid;
         END IF;
  END IF;
  IF (old.stype = '学硕' AND old.cid IS NOT NULL AND new.cid IS NULL)
    Then IF EXISTS(SELECT * from Fee where Fee.tid = old.tid and Fee.occupy_Postgraduate - 1 >= Fee.free_Postgraduate)
           Then UPDATE Fee SET Fee.occupy_Postgraduate = Fee.occupy_Postgraduate - 1, Fee.Total_Price = Fee.Total_Price - 4*Fee.unit_Price
                WHERE Fee.tid = old.tid;
         ELSE
            UPDATE Fee SET Fee.occupy_Postgraduate = Fee.occupy_Postgraduate - 1
            WHERE Fee.tid = old.tid;
         END IF;
  END IF;
  IF (old.stype in ('非全日制工硕', '全日制工硕')  AND old.cid IS NOT NULL AND new.cid IS NULL)
    Then  UPDATE Fee SET Fee.occupy_Other = Fee.occupy_Other - 1, Fee.Total_Price = Fee.Total_Price - 4*Fee.unit_Price
          WHERE Fee.tid = old.tid;
  END IF;
END;

