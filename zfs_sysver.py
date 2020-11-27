import os
import sys
import json
import ConfigParser
import fbrm_dbms
import datetime

class zfs_sys():
    def __init__(self,zfs):
        self.zfs=zfs
        self.cfg = self.get_cfg()
        self.common_cmd = self.get_common_cmd()
        self.set_path()
        self.db = fbrm_dbms.fbrm_db()
        self.today = datetime.datetime.now()
        self.fbrm_datetime = self.today.strftime('%Y-%m-%d %H:%M:%S')

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
    def to_local_time(self,utc):
        """
        Thu Nov 15 2018 23:10:39 GMT+0000 (UTC)
        :param utc:
        :return:
        Thu Nov 15 2018 23:10:39 GMT+0000 (UTC)
        """
        utc_time = datetime.datetime.strptime(utc,"%a %b %d %Y %H:%M:%S GMT+0000 (UTC)")
        local_time = utc_time + datetime.timedelta(hours=9)
        return local_time.strftime('%Y-%m-%d %H:%M:%S')



    def get_cluster(self,asn):
        print '#'*50
        print 'system asn'
        print '#' * 50

        print 'asn :',asn
        pool_cmd='/api/hardware/v1/cluster'
        cmd=self.common_cmd+pool_cmd
        print cmd
        ret=os.popen(cmd).read()
        print ret
        cluster_json=self.get_json(ret)
        print cluster_json
        cluster_list=[]

        resource_list=[]
        cluster_dict = {}
        for cluster in cluster_json['cluster']:

            cluster_dict['asn'] = asn
            cluster_dict['fbrm_date'] = self.fbrm_datetime
            print '-'*50
            print cluster
            print cluster_json['cluster'][cluster]
            if not cluster == 'resources':
                val = cluster_json['cluster'][cluster]
                print 'val :',val,type(val)
                if "'" in val :
                    val=val.replace("'","`")
                if "[" in val:
                    val=','.join(list(val))

                cluster_dict[cluster] = str(val)

            else:

                resource_dict = {}
                resouces  = cluster_json['cluster'][cluster]

                for resource in resouces:
                    print resource.keys()
                    print resource.values()

                    res_dict = {}
                    res_dict['asn'] = asn
                    for key in resource.keys():
                        val = resource[key]
                        if "'" in val:
                            val=val.replace("'","`")
                        if type(val) == type([]):
                            val = ','.join(val)

                        res_dict[key] = val
                        res_dict['fbrm_date'] = self.fbrm_datetime
                    resource_list.append(res_dict)
        cluster_list.append(cluster_dict)
        print cluster_list
        print resource_list
        db_name = 'master.master_zfs_cluster'
        self.db.dbInsertList(cluster_list, db_name)
        db_name = 'master.master_zfs_cluster_resouces'
        self.db.dbInsertList(resource_list, db_name)

    def get_sysver(self,zfs_info):
        return zfs_info['asn']

    def main(self):
        zfs_list=[]
        url='/api/system/v1/version'
        cmd=self.common_cmd + url
        print cmd
        ret=os.popen(cmd).read()
        root=self.get_json(ret)

        print type(root)
        zfs_info= root['version']
        zfs_info['zfs_name'] = self.zfs['name']
        zfs_info['zfs_ip'] = self.zfs['ip']
        zfs_info['fbrm_date'] = self.today.strftime('%Y-%m-%d %H:%M:%S')
        zfs_list.append(zfs_info)

        print zfs_info
        urn =  zfs_info['urn']
        urn = urn.split(':')[-1]
        zfs_info['urn'] = urn

        install_time = zfs_info['install_time']
        zfs_info['install_time'] = self.to_local_time(install_time)
        boot_time   = zfs_info['boot_time']
        zfs_info['boot_time'] = self.to_local_time(boot_time)
        update_time = zfs_info['update_time']
        zfs_info['update_time'] = self.to_local_time(update_time)
        print 'update_time :',update_time
        print 'update_time :',self.to_local_time(update_time)
        self.db.dbInsertList(zfs_list,'master.master_zfs_info')

        asn = zfs_info['asn']
        self.get_cluster(asn)

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
            zfs_sys(zfs).main()


if __name__=='__main__':
    Manager().main()