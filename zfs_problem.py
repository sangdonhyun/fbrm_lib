
import os
import sys
import json
import ConfigParser
import fbrm_dbms
import datetime
import time
class zfs_problem():
    def __init__(self,zfs):
        self.zfs=zfs
        self.cfg = self.get_cfg()
        self.common_cmd = self.get_common_cmd()
        self.set_path()
        self.db = fbrm_dbms.fbrm_db()
        self.today = datetime.datetime.now()
        self.to_day_d=self.today.strftime('%Y-%m-%d')
        self.zfs_ip = self.zfs['ip']
        self.zfs_name= self.zfs['name']
    def set_path(self):
        curl_path=self.cfg.get('common','curl_path')
        path = os.environ['PATH']
        os.environ['PATH'] = '{};{}'.format(curl_path,path)
    def get_common_cmd(self):
        cmd="curl --user {}:{} -k -i https://{}:{}".format(self.zfs['user'],self.zfs['passwd'],self.zfs['ip'],self.zfs['port'])
        return cmd
    def get_cfg(self):
        cfg=ConfigParser.RawConfigParser()
        cfgFile=os.path.join('config','config.cfg')
        cfg.read(cfgFile)
        return cfg
    def get_json(self,ret):
        lineset=list(ret)
        for i in range(len(lineset)):
            ch=lineset[i]
            if ch == '{':
                json_data=''.join(lineset[i:])
                break
        json_ret=json.loads(json_data)
        return json_ret
    def set_colon(self,dict):
        for key in dict.keys():
            val=  dict[key]
            val= val.replace('\'','`')
            val = val.replace('\"', '~')
            dict[key] = val
        return dict
    def set_utf(self,info):
        for key in info.keys():
            if isinstance(info[key],unicode):
                info[key] = info[key].encode("utf-8")
        return info
    def main(self):
        problem_list=[]
        url='/api/problem/v1/problems'
        cmd=self.common_cmd + url
        print cmd
        ret=os.popen(cmd).read()
        root=self.get_json(ret)
        print root
        for problem in root['problems']:
            print problem
            problem = self.set_colon(problem)
            problem['fbrm_date'] = self.to_day_d
            problem['ins_date_time'] = self.today.strftime('%Y-%m-%d %H:%M:%S')
            problem['zfs_name'] = self.zfs_name
            problem['zfs_ip'] = self.zfs_ip
            problem_list.append(self.set_utf(problem))
        self.db.dbInsertList(problem_list,'event.evt_zfs_problem')
class Manager():
    def __init__(self):
        self.zfs_list=self.get_zfs_list()
    def get_zfs_list(self):
        cfg_file=os.path.join('config','list.cfg')
        cfg=ConfigParser.RawConfigParser()
        cfg.read(cfg_file)
        zfs_list=[]
        for sec in cfg.sections():
            zfs={}
            zfs['name']=sec
            for opt in cfg.options(sec):
                zfs[opt]=cfg.get(sec,opt)
            zfs_list.append(zfs)
        return zfs_list
    def main(self):
        for zfs in self.zfs_list:
            try:
                zfs_problem(zfs).main()
            except:
                pass

if __name__=='__main__':
    while True:
        try:
            Manager().main()
        except:
            pass
        time.sleep(60)