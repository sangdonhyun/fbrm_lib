import os
import json
import ConfigParser
import sys
import fbrm_dbms
import daily_table_create
import datetime
import time
class zfs_pools():
    def __init__(self,zfs):
        self.cfg=self.get_cfg()
        self.set_path()
        self.zfs=zfs
        self.common_cmd=self.get_common_cmd()
        self.set_pool_list = []
        self.set_prj_list = []
        self.set_fs_list = []
        self.set_snapshot_list = []
        self.db=fbrm_dbms.fbrm_db()
        self.tb_c=daily_table_create.table_create()
        self.ins_date=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')


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




    def get_pool(self):
        print '#'*50
        print 'POOLS'
        print '#' * 50
        pool_cmd='/api/storage/v1/pools'
        cmd=self.common_cmd+pool_cmd
        print cmd
        ret=os.popen(cmd).read()
        print ret
        pool_json=self.get_json(ret)
        # print pool_json
        self.pools_href_list=[]
        for pool in pool_json['pools']:
            print pool
            self.pools_href_list.append(pool['href'])
            self.set_pool_list.append(pool)


    def get_projects(self):
        print '#'*50
        print 'PROJECTS'
        print '#' * 50
        self.prj_href_list=[]
        print self.pools_href_list
        for href in self.pools_href_list:
            project_cmd= href+'/projects'

            cmd = self.common_cmd + project_cmd
            print cmd
            ret = os.popen(cmd).read()
            # print ret
            projects_json = self.get_json(ret)
            print projects_json

            for prj in projects_json['projects']:
                self.set_prj_list.append(prj)
                href= prj['href']
                self.prj_href_list.append(href)



    def get_filesystems(self):
        print '#'*50
        print 'FILE SYSTEM'
        print '#' * 50
        self.fs_href_list=[]
        for href in self.prj_href_list:
            print href
            cmd=self.common_cmd+href+'/filesystems'
            print cmd
            ret = os.popen(cmd).read()
            # print ret
            fs_json = self.get_json(ret)
            print fs_json
            for fs in fs_json['filesystems']:
                self.set_fs_list.append(fs)
                href=fs['href']
                self.fs_href_list.append(href)


    def get_snapshots(self):
        print '#' * 50
        print 'SNAPSHOTS'
        print '#' * 50

        for href in self.fs_href_list:
            print href
            cmd = self.common_cmd + href + '/snapshots'
            print cmd
            ret = os.popen(cmd).read()
            # print ret
            root = self.get_json(ret)
            print root['snapshots']
            for snap in root['snapshots']:
                self.set_snapshot_list.append(snap)

    def set_projects(self):
        print '#' * 50
        print 'PROJECTS SET '
        print '#' * 50
        print 'projects count :',len(self.set_pool_list)
        prj_dict_list=[]
        for prj in self.set_prj_list:
            print prj
            prj_dict={}
            del prj ['source']
            prj['zfs_name'] = self.zfs['name']
            prj['zfs_ip'] = self.zfs['ip']
            prj['space_data'] = str(int(prj['space_data']))
            prj['space_total'] = str(int(prj['space_total']))
            prj['space_available'] = str(int(prj['space_available']))
            prj['space_snapshots'] = str(int(prj['space_snapshots']))
            prj['fbrm_date'] = self.tb_c.to_day_d
            prj['ins_date_time'] = self.ins_date
            create_str = prj['creation']
            "20200319T06:47:06"
            create_date = datetime.datetime.strptime(create_str, "%Y%m%dT%H:%M:%S").strftime('%Y-%m-%d %H:%M:%S')
            prj['creation'] = create_date


            prj_dict_list.append(prj)
        # tb_name = 'zfs_projects_realtime'
        # tb_name_y = 'fbrm.' + tb_name + "_" + self.tb_c.to_day_y
        # self.tb_c.is_table_tb(tb_name)
        #
        # self.db.dbInsertList(prj_dict_list, tb_name_y)

        tb='live.live_zfs_projects'
        self.db.dbInsertList(prj_dict_list, tb)
        store_prj_dict_list = self.set_store_list(prj_dict_list)
        tb = 'store.store_day_zfs_projects'
        self.db.dbInsertList(store_prj_dict_list, tb)

    def set_pool(self):
        print '#' * 50
        print 'POOLS SET '
        print '#' * 50
        print len(self.set_pool_list)
        pool_dict_list=[]
        for pool in self.set_pool_list:
            pool_dict={}
            keys=pool.keys()
            vals=pool.values()
            u_keys,u_vals=[],[]
            for i in range(len(keys)):
                key=keys[i]
                val=vals[i]
                if key=='usage':
                    # print pool['usage']
                    u_keys = pool['usage'].keys()
                    u_vals = pool['usage'].values()
                else:
                    pool_dict[key]=val

            for i in range(len(u_keys)):
                u_key=u_keys[i]
                u_val=u_vals[i]
                key='u_{}'.format(u_key)
                pool_dict[key] = str(int(u_val))
                print type(pool_dict[key]),pool_dict[key]
            pool_dict['zfs_name'] = self.zfs['name']
            pool_dict['zfs_ip'] = self.zfs['ip']
            pool_dict['fbrm_date'] = self.tb_c.to_day_d
            pool_dict['ins_date_time'] = self.ins_date
            print pool_dict
            pool_dict_list.append(pool_dict)
        # tb_name='zfs_pools_realtime'
        # tb_name_y='fbrm.'+tb_name  + "_"+self.tb_c.to_day_y
        # self.tb_c.is_table_tb(tb_name)
        # self.db.dbInsertList(pool_dict_list,tb_name_y)

        tb='live.live_zfs_pools'
        self.db.dbInsertList(pool_dict_list, tb)
        store_pool_dict_list = self.set_store_list(pool_dict_list)
        tb='store.store_day_zfs_pools'
        self.db.dbInsertList(store_pool_dict_list, tb)


    def set_str(self,src_dict):
        keys=src_dict.keys()
        vals = src_dict.keys()
        for i in range(len(keys)):
            k=keys[i]
            v=vals[i]
            if type(v) == dict:
                src_dict[k] = str(v)
        return src_dict


    def set_store_list(self,live_list):
        store_list = []
        for item in live_list:
            item['store_date'] = item['fbrm_date']
            item['write_date'] = item['ins_date_time']
            store_list.append(item)
        return store_list

    def set_filesystems(self):
        print '#' * 50
        print 'FILESYSTEMS SET '
        print '#' * 50
        print len(self.set_fs_list)
        pool_fs_list = []
        for fs in self.set_fs_list:
            print fs
            del fs['source']
            fs['zfs_name']= self.zfs['name']
            fs['zfs_ip'] = self.zfs['ip']
            fs['space_total'] = str(int(fs['space_total']))
            fs['space_available'] = str(int(fs['space_available']))
            fs['space_data'] = str(int(fs['space_data']))
            fs['space_snapshots'] = str(int(fs['space_snapshots']))
            fs['fbrm_date'] =self.tb_c.to_day_d
            fs['ins_date_time'] = self.ins_date
            fs=self.set_str(fs)
            print type(fs['root_acl'])
            fs['root_acl'] = str(fs['root_acl'])
            print type(fs['root_acl'])
            print fs['root_acl']
            del fs['root_acl']
            create_str = fs['creation']
            "20200319T06:47:06"
            create_date = datetime.datetime.strptime(create_str, "%Y%m%dT%H:%M:%S").strftime('%Y-%m-%d %H:%M:%S')
            fs['creation'] = create_date

            # fs['root_acl'] = str("'{}'".format()['root_acl'])

            pool_fs_list.append(fs)
        # tb_name = 'zfs_filesystems_realtime'
        # tb_name_y = 'fbrm.' + tb_name + "_" + self.tb_c.to_day_y
        # self.tb_c.is_table_tb(tb_name)
        # self.db.dbInsertList(pool_fs_list,tb_name_y)

        tb= 'live.live_zfs_filesystems'
        self.db.dbInsertList(pool_fs_list, tb)

        store_fs_list = self.set_store_list(pool_fs_list)
        tb = 'store.store_day_zfs_filesystems'
        self.db.dbInsertList(store_fs_list, tb)

    def set_snapshots(self):
        print '#' * 50
        print 'SNAPSHOTS SET '
        print '#' * 50
        pool_snapshot_list = []

        for snapshot in self.set_snapshot_list:
            print snapshot

            snapshot['space_data'] = str(int(snapshot['space_data']))
            snapshot['zfs_name'] = self.zfs['name']
            snapshot['zfs_ip'] = self.zfs['ip']
            snapshot['fbrm_date'] = self.tb_c.to_day_d
            snapshot['ins_date_time'] = self.ins_date
            create_str= snapshot['creation']
            "20200319T06:47:06"
            create_date=datetime.datetime.strptime(create_str,"%Y%m%dT%H:%M:%S").strftime('%Y-%m-%d %H:%M:%S')
            snapshot['creation'] = create_date
            pool_snapshot_list.append(snapshot)

        # tb_name = 'zfs_snapshots_realtime'
        # tb_name_y = 'fbrm.' + tb_name + "_" + self.tb_c.to_day_y
        # self.tb_c.is_table_tb(tb_name)
        # self.db.dbInsertList(pool_snapshot_list, tb_name_y)

        tb='live.live_zfs_snapshots'
        self.db.dbInsertList(pool_snapshot_list, tb)
        store_pool_snapshot_list = self.set_store_list(pool_snapshot_list)
        tb = 'store.store_day_zfs_snapshots'
        self.db.dbInsertList(store_pool_snapshot_list, tb)
    def get_network_interfaces(self):
        net_cmd='/api/network/v1/interfaces'
        cmd = self.common_cmd + net_cmd
        ret=os.popen(cmd).read()

        print ret
        interfaces = self.get_json(ret)


        v4addr_list = []
        """
        zfs_name
        zfs_default_ip
        zfs_service_ip
        """
        zfs_network_interfaces=[]
        for val in interfaces['interfaces']:
            print val['v4addrs']
            service_ip={}
            for v4addr in val['v4addrs']:
                service_ip['zfs_name'] = self.zfs['name']
                service_ip['zfs_default_ip'] = self.zfs['ip']

                print v4addr


                if '/' in v4addr:
                    zfs_service_ip=v4addr.split('/')[0]
                else:
                    zfs_service_ip = v4addr
                service_ip['zfs_service_ip'] = zfs_service_ip
                service_ip['fbrm_date'] =self.tb_c.to_day_d
                zfs_network_interfaces.append(service_ip)
        tb_name = 'live.live_zfs_network_interfaces'
        self.db.dbInsertList(zfs_network_interfaces,tb_name)


    def main(self):
        print 'zfs_pool'
        print self.zfs
        print self.common_cmd
        self.get_pool()
        self.set_pool()
        self.get_network_interfaces()
        self.get_projects()
        self.set_projects()
        self.get_filesystems()
        self.set_filesystems()
        self.get_snapshots()
        self.set_snapshots()


    def set_path(self):
        curl_path=self.cfg.get('common','curl_path')
        path = os.environ['PATH']
        os.environ['PATH'] = '{};{}'.format(curl_path,path)


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

            zfs_pools(zfs).main()


if __name__=='__main__':
    Manager().main()
    # cnt =1
    # while True:
    #     Manager().main()
    #     print '-'*50
    #     print datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    #     print 'CNT :',cnt
    #     print '-'*50
    #     time.sleep(60)
    #     cnt = cnt+1

