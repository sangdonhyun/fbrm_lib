import datetime
import fbrm_dbms
import os
import datetime
import time
os.chdir('D:\\Fleta\\Project\\ibrm_lib\\fbrm_lib\\')
class target():
    def __init__(self):
        self.now = datetime.datetime.now()
        self.today_hour = self.now.strftime('%Y-%m-%d 07')
        self.db = fbrm_dbms.fbrm_db()
    def tot_exe_query (self):
        query = """UPDATE store.store_day_zfs_pools aa SET target_yn='Y' FROM (
SELECT min(ins_date_time) ins_date_time ,asn,name FROM store.store_day_zfs_pools sdzp  WHERE substring(ins_date_time,12,2) = '07'  GROUP BY substr(ins_date_time,0,14),asn,name
) bb WHERE bb.asn = aa.asn AND aa.ins_date_time = bb.ins_date_time and aa.name = bb.name
                """
        self.db.queryExec(query)
        return query
    def today_get_7hour_query(self):
        to_day = datetime.datetime.now().strftime('%Y-%m-%d')
        query = """UPDATE store.store_day_zfs_pools aa SET target_yn='Y' FROM (
            SELECT min(ins_date_time) ins_date_time ,asn,name FROM store.store_day_zfs_pools sdzp  WHERE substring(ins_date_time,12,2) = '07' and ins_date_time like '%{}' GROUP BY asn,name
        ) bb WHERE bb.asn = aa.asn AND aa.ins_date_time = bb.ins_date_time and aa.name = bb.name
                        """.format(self.today_hour,to_day)
        self.db.queryExec(query)
        return query
    def today_get_hour_qeury(self):
        to_day = datetime.datetime.now().strftime('%Y-%m-%d')
        query = """
        UPDATE store.store_day_zfs_pools aa SET target_yn='Y' FROM (
            SELECT min(ins_date_time) ins_date_time ,asn,name FROM store.store_day_zfs_pools sdzp  WHERE substring(ins_date_time,12,2) >= '07' and fbrm_date = '{}'  GROUP BY asn,name
        ) bb WHERE bb.asn = aa.asn AND aa.ins_date_time = bb.ins_date_time and aa.name = bb.name
        """.format(to_day)
        self.db.queryExec(query)
        print query
    def get_today_count(self):
        query = "select count(*) from store.store_day_zfs_pools where ins_date_time like '{}%'".format(self.today_hour)
        print (query)
        ret= self.db.getRaw(query)
        return ret[0][0]
    def main(self):
        cnt = self.get_today_count()
        print 'cnt :',cnt
        if cnt  > 0:
            self.today_get_7hour_query()
        else:
            self.today_get_hour_qeury()
if __name__=='__main__':
    # target().tot_exe_query()
    target().main()

