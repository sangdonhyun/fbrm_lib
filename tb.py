'''
Created on 2020. 4. 6.

@author: user
'''
import os
import glob
import sys
import fbrm_dbms
import datetime

csv_file='C:\\Fleta\\data\\ZFS_MON\\linux68_cat.csv'

class fbrm_rman():
    def __init__(self):
        self.db=fbrm_dbms.fbrm_db()
        self.key_set=self.key_set()
    
    def getCfg(self):
        pass
    
    
    def str_to_list(self,srt):
        
        cat_list=[]
        for cat in srt.split(','):
            cat_list.append(cat.strip())
        
        return cat_list
    
    
    def key_set(self):
        keystr="""DB_KEY    NUMBER            22            N
DB_NAME    VARCHAR2            8            N
SESSION_KEY    NUMBER            22            Y
SESSION_RECID    NUMBER            22            Y
SESSION_STAMP    NUMBER            22            Y
COMMAND_ID    VARCHAR2            33            Y
START_TIME    DATE            7            Y
END_TIME    DATE            7            Y
INPUT_BYTES    NUMBER            22            Y
OUTPUT_BYTES    NUMBER            22            Y
STATUS_WEIGHT    NUMBER            22            Y
OPTIMIZED_WEIGHT    NUMBER            22            Y
INPUT_TYPE_WEIGHT    NUMBER            22            Y
OUTPUT_DEVICE_TYPE    VARCHAR2            17            Y
AUTOBACKUP_COUNT    NUMBER            22            Y
BACKED_BY_OSB    VARCHAR2            3            Y
AUTOBACKUP_DONE    VARCHAR2            3            Y
STATUS    VARCHAR2            23            Y
INPUT_TYPE    VARCHAR2            13            Y
OPTIMIZED    VARCHAR2            3            Y
ELAPSED_SECONDS    NUMBER            22            Y
COMPRESSION_RATIO    NUMBER            22            Y
INPUT_BYTES_PER_SEC    NUMBER            22            Y
OUTPUT_BYTES_PER_SEC    NUMBER            22            Y
INPUT_BYTES_DISPLAY    VARCHAR2            4000            Y
OUTPUT_BYTES_DISPLAY    VARCHAR2            4000            Y
INPUT_BYTES_PER_SEC_DISPLAY    VARCHAR2            4000            Y
OUTPUT_BYTES_PER_SEC_DISPLAY    VARCHAR2            4000            Y
TIME_TAKEN_DISPLAY    VARCHAR2            4000            Y"""
        key_set=[]
        for line in keystr.splitlines():
            key_set.append(line.split())
        return key_set
    
    def null_check(self,arg):
        for key in self.key_set:
            if key[0]== arg:
                return key[1],key[3]
        return None,None
    
    def main(self):
        now=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        line_bit=False
        head=''
        with open(csv_file) as f:
            frd=f.read()
        num=0
        arg=''
        argList=[]
        lineset=frd.splitlines()
        linefeed='----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------'
        
        lineset=lineset[40:]
        tot=len(lineset)
        for i in range(len(lineset)):
            line=lineset[i]
            if i % 4 == 0:
#                 print line
#                 print lineset[i+1].strip(),len(lineset[i+1].strip())
#                 print lineset[i+2].strip(),len(lineset[i+2].strip())
                
                if i+2 <= tot:
                    arg=line+','+lineset[i+1].strip()+','+lineset[i+2].strip()
                    arg_list=self.str_to_list(arg)
                    if len(arg_list) > 30:
                        
                        argList.append(arg_list)
                
#         print argList[0]
        """
        "HOSTNAME", "AGENT_IP", "DB_KEY", "DB_NAME", "SESSION_KEY", "SESSION_RECID", 
       "SESSION_STAMP", "COMMAND_ID", "START_TIME", "END_TIME", "INPUT_BYTES", 
       "OUTPUT_BYTES", "STATUS_WEIGHT", "OPTIMIZED_WEIGHT", "INPUT_TYPE_WEIGHT", 
       "OUTPUT_DEVICE_TYPE", "AUTOBACKUP_COUNT", "BACKED_BY_OSB", "AUTOBACKUP_DONE", 
       "STATUS", "INPUT_TYPE", "OPTIMIZED", "ELAPSED_SECONDS", "COMPRESSION_RATIO", 
       "INPUT_BYTES_PER_SEC", "OUTPUT_BYTES_PER_SEC", "INPUT_BYTES_DISPLAY", 
       "OUTPUT_BYTES_DISPLAY", "INPUT_BYTES_PER_SEC_DISPLAY", "OUTPUT_BYTES_PER_SEC_DISPLAY", 
       "TIME_TAKEN_DISPLAY", "COLLECT_TIME"
        """
        cat_info_list=[]
        
        for arg in argList:
            
            cat_info={}
            cat_info['HOSTNAME']=arg[0]
            cat_info['AGENT_IP']=arg[1]
            cat_info['DB_KEY']=arg[2]
            cat_info['DB_NAME']=arg[3]
            cat_info['SESSION_KEY']=arg[4]
            cat_info['SESSION_RECID']=arg[5]
            if arg[6] == '':
                arg[6]=0
            cat_info['SESSION_STAMP']=arg[6]
            cat_info['COMMAND_ID']=arg[7]
            cat_info['START_TIME']=arg[8]
            
            cat_info['END_TIME']=arg[9]
            if arg[10] == '':
                arg[10]=0
            cat_info['INPUT_BYTES']=arg[10]
            if arg[11] == '':
                arg[11]=0
            cat_info['OUTPUT_BYTES']=arg[11]
            if arg[12] == '':
                arg[12]=0
            cat_info['STATUS_WEIGHT']=arg[12]
            if arg[13] == '':
                arg[13]=0
            cat_info['OPTIMIZED_WEIGHT']=arg[13]
            if arg[14] == '':
                arg[14]=0
            cat_info['INPUT_TYPE_WEIGHT']=arg[14]
            cat_info['OUTPUT_DEVICE_TYPE']=arg[15]
            cat_info['AUTOBACKUP_COUNT']=arg[16]
            cat_info['BACKED_BY_OSB']=arg[17]
            cat_info['AUTOBACKUP_DONE']=arg[18]
            cat_info['STATUS']=arg[19]
            cat_info['INPUT_TYPE']=arg[20]
            cat_info['OPTIMIZED']=arg[21]
            if arg[22] == '':
                arg[22]=0
            cat_info['ELAPSED_SECONDS']=arg[22]
            
            cat_info['COMPRESSION_RATIO']=arg[23]
            if arg[24] == '':
                arg[24]=0
            cat_info['INPUT_BYTES_PER_SEC']=arg[24]
            if arg[25] == '':
                arg[25]=0
            cat_info['OUTPUT_BYTES_PER_SEC']=arg[25]
            cat_info['INPUT_BYTES_DISPLAY']=arg[26]
            cat_info['OUTPUT_BYTES_DISPLAY']=arg[27]
            cat_info['INPUT_BYTES_PER_SEC_DISPLAY']=arg[28]
            cat_info['OUTPUT_BYTES_PER_SEC_DISPLAY']=arg[29]
            cat_info['TIME_TAKEN_DISPLAY']=arg[30]
            cat_info['COLLECT_TIME']=now
            cat_info_list.append(cat_info)

        self.db.queryExec("delete from fbrm.mon_rman_backup_list")
        self.db.dbInsertList(cat_info_list, 'fbrm.mon_rman_backup_list')
        for cat_info in cat_info_list:
            print cat_info
         
        
        

if __name__=='__main__':
    fbrm_rman().main()