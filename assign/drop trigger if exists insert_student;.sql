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

