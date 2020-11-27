import os
import datetime
import fbrm_dbms

class table_create():
    def __init__(self):
        self.db=fbrm_dbms.fbrm_db()
        self.now = datetime.datetime.now()
        self.to_day_d = self.now.strftime('%Y-%m-%d')
        self.to_day_y = self.now.strftime('y%Ym%md%d')

    def is_table_tb(self,tb_name):
        print 'tb_name : ',tb_name

        tb_name_y = tb_name + "_%s"%self.to_day_y
        sql="select count(*) from pg_tables where tablename = 'fbrm.{tb_name}'"

        sql = sql.format(tb_name=tb_name_y)
        print sql
        ret_cnt=self.db.getRaw(sql)[0][0]
        print 'ret_cnt :',ret_cnt
        if ret_cnt == 0:
            self.table_create(tb_name)



    def table_create(self,tb_name):
        tb_name_y = tb_name + "_%s"%self.to_day_y
        print tb_name
        print tb_name_y
        sql="""
        CREATE TABLE fbrm.{tb_name}_{date_y}
(
    
    CONSTRAINT {date_y} CHECK (fbrm_date >= '{date_d}'::date)
)
    INHERITS (fbrm.{tb_name})
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE fbrm.{tb_name}_{date_y}
    OWNER to fbrmuser;
        """
        sql=sql.format(date_d=self.to_day_d,date_y=self.to_day_y,tb_name=tb_name)
        print sql
        self.db.dbQeuryIns(sql)

        day_1 = self.now - datetime.timedelta(days=1)
        day_2 = self.now - datetime.timedelta(days=2)
        day_1_d = day_1.strftime('%Y-%m-%d')
        day_2_d = day_2.strftime('%Y-%m-%d')
        day_1_y = day_1.strftime('y%Ym%md%d')
        day_2_y = day_2.strftime('y%Ym%md%d')
        trigger_sql ="""
CREATE OR REPLACE FUNCTION fbrm.{tb_name}_trigger()
    RETURNS trigger
    LANGUAGE 'plpgsql'
    COST 100
    VOLATILE NOT LEAKPROOF
AS $BODY$
BEGIN
    IF ( NEW.fbrm_date = DATE '{date_d}') THEN
    INSERT INTO fbrm.{tb_name}_{date_y} VALUES (NEW.*);
ELSIF ( NEW.fbrm_date = DATE '{date_1_d}') THEN
    INSERT INTO fbrm.{tb_name}_{date_1_y} VALUES (NEW.*);
ELSIF ( NEW.fbrm_date = DATE '{date_2_d}') THEN
    INSERT INTO fbrm.{tb_name}_{date_2_y} VALUES (NEW.*);
ELSE
RAISE EXCEPTION 'Date out of range.  Fix the zfs_filesystems_realtime_trigger() function!';
END IF;
RETURN NULL;
END;
$BODY$;

ALTER FUNCTION fbrm.{tb_name}_trigger()
    OWNER TO fbrmuser;

        
        """
        trigger_sql = trigger_sql.format(date_d=self.to_day_d,date_y=self.to_day_y,date_1_d=day_1_d,date_1_y=day_1_y,date_2_d=day_2_d,date_2_y=day_2_y,tb_name=tb_name,tb_name_y=tb_name_y)
        print trigger_sql
        self.db.queryExec(trigger_sql)



if __name__=='__main__':
    tb_create=table_create()
    tb_name='mon_zfs_filesystem_realtime'
    tb_create.is_table_tb(tb_name)