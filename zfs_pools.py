# -*-coding:utf-8-*-
import os
import json
import ConfigParser
import sys
import fbrm_dbms
import daily_table_create
import datetime
import time
import threading


class zfs_pools():
    def __init__(self, zfs):
        self.cfg = self.get_cfg()
        self.set_path()
        self.zfs = zfs
        self.common_cmd = self.get_common_cmd()
        self.set_pool_list = []
        self.set_prj_list = []
        self.set_fs_list = []
        self.set_snapshot_list = []
        self.db = fbrm_dbms.fbrm_db()
        self.tb_c = daily_table_create.table_create()
        self.ins_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.today = datetime.datetime.now()

        # os.chdir("E:\\PycharmProjects\\fbrm_lib")

    #        self.cluster_name = self.get_cluster_name(self.zfs['name'])
    def del_arg(self, asn_list, arg='pools'):
        asn_str = "','".join(asn_list)
        print asn_str
        asns = "'{}'".format(asn_str)
        print asns
        if len(asn_list) > 0:
            query = "delete from live.live_zfs_{} where asn in ({})".format(arg, asns)
            print query
            self.db.queryExec(query)

    def get_cluster_name(self, node_name):
        query = """select cluster_name from master.master_zfs_cluster  where node_name ='{}' """.format(node_name)
        # print query
        ret = self.db.getRaw(query)
        # print ret
        if len(ret) > 0:
            cluster_name = ret[0][0]
        else:
            cluster_name = ''
        return cluster_name

    def get_common_cmd(self):
        cmd = "curl --user {}:{} -k -i https://{}:{}".format(self.zfs['user'], self.zfs['passwd'], self.zfs['ip'],
                                                             self.zfs['port'])
        return cmd

    def get_cfg(self):
        cfg = ConfigParser.RawConfigParser()
        cfgFile = os.path.join('config', 'config.cfg')
        cfg.read(cfgFile)
        return cfg

    def get_json(self, ret):
        lineset = list(ret)
        for i in range(len(lineset)):
            ch = lineset[i]
            if ch == '{':
                json_data = ''.join(lineset[i:])
                break
        json_ret = json.loads(json_data)
        self.fwrite(ret)
        return json_ret

    def get_pool(self):
        print '#' * 50
        print 'POOLS'
        print '#' * 50
        pool_cmd = '/api/storage/v1/pools'
        cmd = self.common_cmd + pool_cmd
        print cmd
        ret = os.popen(cmd).read()
        # print ret
        pool_json = self.get_json(ret)
        # print pool_json
        self.pools_href_list = []
        asn_list = []
        for pool in pool_json['pools']:
            print pool
            print 'asn :', pool['asn']
            asn_list.append(pool['asn'])
            self.pools_href_list.append(pool['href'])
            self.set_pool_list.append(pool)
        return asn_list

    def get_projects(self):
        print '#' * 50
        print 'PROJECTS'
        print '#' * 50
        self.prj_href_list = []
        # print self.pools_href_list
        for href in self.pools_href_list:
            project_cmd = href + '/projects'
            # print project_cmd
            cmd = self.common_cmd + project_cmd
            print cmd
            ret = os.popen(cmd).read()
            # print ret
            projects_json = self.get_json(ret)
            if 'projects' in projects_json.keys():
                for prj in projects_json['projects']:
                    self.set_prj_list.append(self.set_utf(prj))
                    href = prj['href'].encode('utf-8')
                    self.prj_href_list.append(href)

    def get_filesystems(self):
        print '#' * 50
        print 'FILE SYSTEM'
        print '#' * 50
        self.fs_href_list = []
        for href in self.prj_href_list:
            # print href
            cmd = self.common_cmd + href + '/filesystems'
            print cmd
            ret = os.popen(cmd).read()
            # print ret
            fs_json = self.get_json(ret)
            # print fs_json
            for fs in fs_json['filesystems']:
                self.set_fs_list.append(fs)
                href = fs['href']
                self.fs_href_list.append(href)

    def get_snapshots(self):
        print '#' * 50
        print 'SNAPSHOTS'
        print '#' * 50
        for href in self.fs_href_list:
            # print href
            cmd = self.common_cmd + href + '/snapshots'
            print cmd
            ret = os.popen(cmd).read()
            # print ret
            root = self.get_json(ret)
            # print root['snapshots']
            for snap in root['snapshots']:
                if not snap['name'][0] == '.':
                    self.set_snapshot_list.append(snap)

    def set_projects(self):
        print '#' * 50
        print 'PROJECTS SET '
        print '#' * 50
        print 'projects count :', len(self.set_pool_list)
        prj_dict_list = []
        query = """select node_name,cluster_name from master.master_zfs_cluster  where asn='{}' """.format(self.asn)
        # print query
        ret = self.db.getRaw(query)
        # print ret
        if len(ret) > 0:
            zfs_name = ret[0][0]
            cluster_name = ret[0][1]
        else:
            zfs_name = ''
            cluster_name = ''
        # self.i_cluster_name, self.cluster_name = zfs_name, cluster_name
        for prj in self.set_prj_list:
            print prj
            prj = self.verification('PROJECTS',prj)
            prj_dict = {}
            # del prj['source']
            prj['zfs_name'] = self.zfs['name']
            prj['node_name'] = self.zfs['name']
            prj['asn'] = self.asn
            prj['zfs_ip'] = self.zfs['ip']
            prj['cluster_ip'] = self.zfs['ip']
            prj['space_data'] = str(round(float(prj['space_data'])))
            prj['space_total'] = str(round(float(prj['space_total'])))
            prj['space_available'] = str(round(float(prj['space_available'])))
            prj['space_snapshots'] = str(round(float(prj['space_snapshots'])))
            prj['space_unused_res_shares'] = str(round(float(prj['space_unused_res_shares'])))

            prj['fbrm_date'] = self.tb_c.to_day_d
            prj['ins_date_time'] = self.ins_date
            create_str = prj['creation']
            "20200319T06:47:06"
            create_date = datetime.datetime.strptime(create_str, "%Y%m%dT%H:%M:%S").strftime('%Y-%m-%d %H:%M:%S')

    def set_pool(self):
        print '#' * 50
        print 'POOLS SET '
        print '#' * 50
        print len(self.set_pool_list)
        query = """select node_name,cluster_name from master.master_zfs_cluster  where asn='{}' """.format(self.asn)
        # print query
        ret = self.db.getRaw(query)
        # print ret
        if len(ret) > 0:
            zfs_name = ret[0][0]
            cluster_name = ret[0][1]
        else:
            zfs_name = ''
            cluster_name = ''
        pool_dict_list = []
        for pool in self.set_pool_list:
            pool = self.verification('POOLS',pool)
            pool_dict = {}
            keys = pool.keys()
            vals = pool.values()
            u_keys, u_vals = [], []
            for i in range(len(keys)):
                key = keys[i]
                val = vals[i]
                if key == 'usage':
                    # print pool['usage']
                    u_keys = pool['usage'].keys()
                    u_vals = pool['usage'].values()
                else:
                    pool_dict[key] = val
            for i in range(len(u_keys)):
                u_key = u_keys[i]
                u_val = u_vals[i]
                key = 'u_{}'.format(u_key)
                pool_dict[key] = str(int(u_val))

            pool_dict['zfs_ip'] = self.zfs['ip']
            pool_dict['cluster_ip'] = self.zfs['ip']
            pool_dict['fbrm_date'] = self.tb_c.to_day_d
            pool_dict['ins_date_time'] = self.ins_date
            pool_dict['zfs_name'] = self.cluster_name
            pool_dict['cluster_name'] = self.cluster_name
            pool_dict['node_name'] = self.zfs['name']
            # print pool_dict
            pool_dict_list.append(self.set_utf(pool_dict))
        # tb_name='zfs_pools_realtime'
        # tb_name_y='fbrm.'+tb_name  + "_"+self.tb_c.to_day_y
        # self.tb_c.is_table_tb(tb_name)
        # self.db.dbInsertList(pool_dict_list,tb_name_y)
        tb = 'live.live_zfs_pools'
        self.db.dbInsertList(pool_dict_list, tb)
        store_pool_dict_list = self.set_store_list(pool_dict_list)
        tb = 'store.store_day_zfs_pools'
        self.db.dbInsertList(store_pool_dict_list, tb)
        return pool_dict_list

    def set_str(self, src_dict):
        keys = src_dict.keys()
        vals = src_dict.keys()
        for i in range(len(keys)):
            k = keys[i]
            v = vals[i]
            if type(v) == dict:
                src_dict[k] = str(v)
        return src_dict

    def set_store_list(self, live_list):
        store_list = []
        for item in live_list:
            item['store_date'] = item['fbrm_date']
            item['write_date'] = item['ins_date_time']
            store_list.append(item)
        return store_list

    def verification(self,arg,tb_dic):
        if arg=='FILESYSTEMS':
            basic_keys=['ins_date_time', 'id', 'canonical_name', 'name', 'pool', 'project', 'mountpoint', 'readlimit', 'effectivereadlimit', 'logbias', 'shareobjectstore', 'nodestroy', 'href', 'casesensitivity', 'utf8only', 'compression', 'sharetftp', 'encryption', 'copies', 'aclinherit', 'compressratio', 'space_total', 'recordsize', 'keychangedate', 'space_available', 'root_permissions', 'space_unused_res', 'maxblocksize', 'rstchown', 'shadow', 'atime', 'space_unused_res_shares', 'root_acl', 'normalization', 'sharesftp', 'reservation_snap', 'effectivewritelimit', 'migration', 'snapdir', 'creation', 'sharenfs', 'sharesmb', 'space_data', 'quota_snap', 'aclmode', 'dedup', 'snaplabel', 'shareftp', 'readonly', 'secondarycache', 'root_user', 'space_snapshots', 'quota', 'exported', 'vscan', 'reservation', 'keystatus', 'writelimit', 'checksum', 'root_group', 'sharedav', 'nbmand', 'zfs_name', 'zfs_ip', 'origin', 'cluster_ip', 'asn', 'origin_project', 'origin_share', 'origin_snapshot', 'origin_pool', 'origin_collection', 'node_name', 'cluster_name']
        elif arg=='POOLS':
            basic_keys=['u_id', 'fbrm_date', 'ins_date_time', 'name', 'asn', 'status', 'profile', 'encryption', 'owner', 'href', 'peer', 'u_available', 'u_usage_snapshots', 'u_usage_metasize', 'u_used', 'u_compression', 'u_usage_child_reservation', 'u_dedupsize', 'u_usage_reservation', 'u_free', 'u_usage_data', 'u_usage_replication', 'u_dedupratio', 'u_usage_metaused', 'u_total', 'u_usage_total', 'zfs_name', 'zfs_ip', 'cluster_ip', 'cluster_name', 'node_name']
        elif arg == 'PROJECTS':
            basic_keys=['fbrm_date', 'ins_date_time', 'name', 'id', 'pool', 'default_volblocksize', 'readlimit', 'logbias', 'shareobjectstore', 'nodestroy', 'href', 'compression', 'sharetftp', 'encryption', 'copies', 'aclinherit', 'compressratio', 'space_total', 'recordsize', 'keychangedate', 'space_available', 'space_unused_res', 'maxblocksize', 'atime', 'default_user', 'space_unused_res_shares', 'default_group', 'sharesftp', 'rstchown', 'sharesmb', 'defaultreadlimit', 'defaultgroupquota', 'creation', 'sharenfs', 'migration', 'default_permissions', 'mountpoint', 'space_data', 'defaultuserquota', 'default_sparse', 'aclmode', 'dedup', 'snaplabel', 'shareftp', 'readonly', 'default_volsize', 'secondarycache', 'space_snapshots', 'quota', 'exported', 'vscan', 'reservation', 'keystatus', 'writelimit', 'checksum', 'canonical_name', 'snapdir', 'defaultwritelimit', 'sharedav', 'nbmand', 'zfs_name', 'zfs_ip', 'source', 'cluster_ip', 'asn', 'node_name', 'cluster_name']
        elif arg == 'SNAPSHOTS':
            basic_keys=['fbrm_date', 'ins_date_time', 'id', 'name', 'pool', 'project', 'numclones', 'creation', 'share', 'collection', 'href', 'space_unique', 'space_data', 'isauto', 'shadowsnap', 'canonical_name', 'type', 'zfs_name', 'zfs_ip', 'cluster_ip', 'asn', 'node_name', 'cluster_name']

        for k in tb_dic.keys():
            if k not in basic_keys:
                del tb_dic[k]
        return tb_dic


    def set_filesystems(self):
        print '#' * 50
        print 'FILESYSTEMS SET '
        print '#' * 50
        print len(self.set_fs_list)
        pool_fs_list = []
        for fs in self.set_fs_list:
            # print fs
            fs = self.verification('FILESYSTEMS',fs)

            fs['zfs_name'] = self.zfs['name']
            fs['node_name'] = self.zfs['name']
            fs['zfs_ip'] = self.zfs['ip']
            fs['asn'] = self.asn

            fs['space_total'] = float(fs['space_total'])
            fs['space_available'] = float(fs['space_available'])
            fs['space_data'] = float(fs['space_data'])
            fs['space_snapshots'] = float(fs['space_snapshots'])
            fs['quota'] = float(fs['quota'])
            fs['maxblocksize'] = float(fs['maxblocksize'])
            fs['reservation'] = float(fs['reservation'])
            fs['space_unused_res'] = str(float(fs['space_unused_res']))
            fs['fbrm_date'] = self.tb_c.to_day_d
            fs['ins_date_time'] = self.ins_date
            fs = self.set_str(fs)
            print type(fs['root_acl'])
            fs['root_acl'] = str(fs['root_acl'])
            print type(fs['root_acl'])
            print fs['root_acl']
            del fs['root_acl']
            create_str = fs['creation']
            "20200319T06:47:06"
            create_date = datetime.datetime.strptime(create_str, "%Y%m%dT%H:%M:%S").strftime('%Y-%m-%d %H:%M:%S')
            fs['creation'] = create_date
            fs['cluster_name'] = self.cluster_name
            if 'origin' in fs.keys():
                origin = fs['origin']
                fs['origin_project'] = origin['project']
                fs['origin_share'] = origin['share']
                fs['origin_snapshot'] = origin['snapshot']
                fs['origin_pool'] = origin['pool']
                fs['origin_collection'] = origin['collection']
                del fs['origin']
            # fs['root_acl'] = str("'{}'".format()['root_acl'])
            print fs
            pool_fs_list.append(self.set_utf(fs))
        # tb_name = 'zfs_filesystems_realtime'
        # tb_name_y = 'fbrm.' + tb_name + "_" + self.tb_c.to_day_y
        # self.tb_c.is_table_tb(tb_name)
        # self.db.dbInsertList(pool_fs_list,tb_name_y)
        tb = 'live.live_zfs_filesystems'
        try:
            self.db.dbInsertList(pool_fs_list, tb)
        except:
            pass

        store_fs_list = self.set_store_list(pool_fs_list)
        tb = 'store.store_day_zfs_filesystems'
        try:
            self.db.dbInsertList(store_fs_list, tb)
        except:
            pass

    def set_snapshots(self):
        print '#' * 50
        print 'SNAPSHOTS SET '
        print '#' * 50
        pool_snapshot_list = []
        for snapshot in self.set_snapshot_list:
            snapshot = self.verification('SNAPSHOTS',snapshot)
            print snapshot
            snapshot['space_data'] = str(int(snapshot['space_data']))
            snapshot['zfs_name'] = self.zfs['name']
            snapshot['node_name'] = self.zfs['name']
            snapshot['zfs_ip'] = self.zfs['ip']
            snapshot['fbrm_date'] = self.tb_c.to_day_d
            snapshot['ins_date_time'] = self.ins_date
            snapshot['asn'] = self.asn
            create_str = snapshot['creation']
            "20200319T06:47:06"
            create_utc_date = datetime.datetime.strptime(create_str, "%Y%m%dT%H:%M:%S")
            create_kst_date = create_utc_date + datetime.timedelta(hours=9)
            create_date = create_kst_date.strftime('%Y-%m-%d %H:%M:%S')
            print('create_str :', create_str)
            print('create_date :', create_date)
            snapshot['creation'] = create_date
            snapshot['cluster_name'] = self.cluster_name
            snapshot['space_unique'] = float(snapshot['space_unique'])
            snapshot['space_data'] = float(snapshot['space_data'])
            if 'retentionpolicy' in snapshot.keys():
                del(snapshot['retentionpolicy'])

            pool_snapshot_list.append(self.set_utf(snapshot))
        # tb_name = 'zfs_snapshots_realtime'
        # tb_name_y = 'fbrm.' + tb_name + "_" + self.tb_c.to_day_y
        # self.tb_c.is_table_tb(tb_name)
        # self.db.dbInsertList(pool_snapshot_list, tb_name_y)
        query = "delete from live.live_zfs_snapshots where node_name = '{}'".format(self.zfs['name'])
        self.db.queryExec(query)
        tb = 'live.live_zfs_snapshots'
        self.db.dbInsertList(pool_snapshot_list, tb)
        store_pool_snapshot_list = self.set_store_list(pool_snapshot_list)
        tb = 'store.store_day_zfs_snapshots'
        self.db.dbInsertList(store_pool_snapshot_list, tb)

    def get_network_interfaces(self):
        net_cmd = '/api/network/v1/interfaces'
        cmd = self.common_cmd + net_cmd
        ret = os.popen(cmd).read()
        print cmd
        interfaces = self.get_json(ret)

        v4addr_list = []
        """
        zfs_name
        zfs_default_ip
        zfs_service_ip
        """
        zfs_network_interfaces = []
        for val in interfaces['interfaces']:
            # print val['v4addrs']
            service_ip = {}
            for v4addr in val['v4addrs']:
                service_ip['zfs_name'] = self.zfs['name']
                service_ip['zfs_default_ip'] = self.zfs['ip']
                # print v4addr

                if '/' in v4addr:
                    zfs_service_ip = v4addr.split('/')[0]
                else:
                    zfs_service_ip = v4addr
                service_ip['zfs_service_ip'] = zfs_service_ip
                service_ip['fbrm_date'] = self.tb_c.to_day_d
                service_ip['zfs_cluster'] = self.asn
                service_ip['node_name'] = self.zfs['name']
                service_ip['asn'] = self.asn
                zfs_network_interfaces.append(self.set_utf(service_ip))
        tb_name = 'live.live_zfs_network_interfaces'
        self.db.dbInsertList(zfs_network_interfaces, tb_name)

    def set_utf(self, info):
        for key in info.keys():
            if isinstance(info[key], unicode):
                info[key] = info[key].encode("utf-8")
        return info

    def set_version(self):
        print '#' * 50
        print 'VERSION'
        print '#' * 50
        zfs_list = []
        pool_cmd = '/api/system/v1/version'
        cmd = self.common_cmd + pool_cmd
        print cmd
        ret = os.popen(cmd).read()
        # print ret
        root = self.get_json(ret)
        zfs_info = root['version']
        zfs_info = root['version']
        zfs_info['zfs_name'] = self.zfs['name']
        zfs_info['zfs_ip'] = self.zfs['ip']
        # zfs_info['cluster_ip'] = self.zfs['ip']
        zfs_info['fbrm_date'] = self.today.strftime('%Y-%m-%d %H:%M:%S')

        zfs_list.append(self.set_utf(zfs_info))
        urn = zfs_info['urn']
        urn = urn.split(':')[-1]
        zfs_info['urn'] = urn
        install_time = zfs_info['install_time']
        zfs_info['install_time'] = self.to_local_time(install_time)
        boot_time = zfs_info['boot_time']
        zfs_info['boot_time'] = self.to_local_time(boot_time)
        update_time = zfs_info['update_time']
        zfs_info['update_time'] = self.to_local_time(update_time)
        # self.db.dbInsertList(zfs_list, 'master.master_zfs_info')
        self.asn = zfs_info['asn']
        self.node_name = zfs_info['nodename']
        self.cluster_name = self.get_cluster()
        # if self.asn =='3e9e38da-8972-4768-99eb-dae2959e85ec':
        #     zfs_name = 'PEDW_HA_01'
        #     cluster_name = 'pzfscl01'
        # elif self.asn =='7430f3fb-c8bf-ec76-d8e1-9a2019310032':
        #     zfs_name = 'PEDW_HA_01'
        #     cluster_name = 'pzfscl02'
        # elif self.asn =='1be8103e-c0cb-40bc-c5f1-b57e93c26ada':
        #     zfs_name = 'PEDW_HA_02'
        #     cluster_name = 'pzfscl03'
        # elif self.asn =='32c442b2-5779-c93b-9301-dc123ff292bb':
        #     zfs_name = 'PEDW_HA_02'
        #     cluster_name = 'pzfscl04'
        # elif self.asn =='5c5bd1d2-402c-65ed-f1a0-fa54bccf3783':
        #     zfs_name = 'PEDW_HA_03'
        #     cluster_name = 'pzfscl05'
        # else :
        #     zfs_name = 'PEDW_HA_03'
        #     cluster_name = 'pzfscl06'

        print '-' * 30
        print 'urn :', urn

    def get_cluster(self):
        query = "SELECT zfs_cluster FROM master.master_zfs_info where asn = '{}'".format(self.asn)
        cluster_name = ''
        try:
            cluster_name = self.db.getRaw(query)[0][0]
        except:
            pass
        return cluster_name

    def del_node_name(self, node_name, arg='pools'):
        query = "delete from live.live_zfs_{} where node_name in ('{}')".format(arg, node_name)
        print query
        self.db.queryExec(query)

    def to_local_time(self, utc):
        """
        Thu Nov 15 2018 23:10:39 GMT+0000 (UTC)
        :param utc:
        :return:
        Thu Nov 15 2018 23:10:39 GMT+0000 (UTC)
        """
        utc_time = datetime.datetime.strptime(utc, "%a %b %d %Y %H:%M:%S GMT+0000 (UTC)")
        local_time = utc_time + datetime.timedelta(hours=9)
        return local_time.strftime('%Y-%m-%d %H:%M:%S')

    def fwrite(self, msg, wbit='a'):
        with open('data.txt', wbit) as f:
            f.write(msg + '/n')

    def main(self):
        print 'zfs_pool'
        print self.zfs
        print self.common_cmd
        self.fwrite('start', 'w')
        self.set_version()
        pools_asn_list = self.get_pool()
        self.del_node_name(self.zfs['name'], 'pools')
        self.set_pool()
        self.get_network_interfaces()
        self.get_projects()
        # self.del_arg(pools_asn_list, 'projects')
        self.del_node_name(self.zfs['name'], 'projects')
        self.set_projects()
        self.get_filesystems()
        self.del_node_name(self.zfs['name'], 'filesystems')
        # self.del_arg(pools_asn_list, 'filesystems')
        self.set_filesystems()
        self.get_snapshots()
        self.del_node_name(self.zfs['name'], 'snapshots')
        # self.del_arg(pools_asn_list, 'snapshots')
        self.set_snapshots()

    def set_path(self):
        curl_path = self.cfg.get('common', 'curl_path')
        path = os.environ['PATH']
        os.environ['PATH'] = '{};{}'.format(curl_path, path)


class Manager():
    def __init__(self):
        self.zfs_list = self.get_zfs_list()
        self.db = fbrm_dbms.fbrm_db()

    def get_zfs_list(self):
        cfg_file = os.path.join('config', 'list.cfg')
        cfg = ConfigParser.RawConfigParser()
        cfg.read(cfg_file)
        zfs_list = []
        for sec in cfg.sections():
            zfs = {}
            zfs['name'] = sec
            for opt in cfg.options(sec):
                zfs[opt] = cfg.get(sec, opt)
            zfs_list.append(zfs)
        return zfs_list

    def set_zfs_serial(self):
        """select asn from live.live_zfs_pools where length(asn) = 36 group by asn
           """
        query = """select asn from live.live_zfs_filesystems where length(asn) = 36 group by asn"""
        print query
        for tb in self.db.getRaw(query):
            asn = tb[0]
            q = """select * from master.mst_cluster where zfs_serial like '%{}%'
                """.format(asn)
            print q
            zfs_serial = self.db.getRaw(q)[0][0]
            print zfs_serial
            q1 = """ UPDATE live.live_zfs_filesystems
         SET asn ='{}' where asn = '{}'""".format(zfs_serial, asn)
            print q1
            self.db.queryExec(q1)
        query = """select asn from live.live_zfs_SNAPSHOTS where length(asn) = 36 group by asn"""
        print query
        for tb in self.db.getRaw(query):
            asn = tb[0]
            q = """select * from master.mst_cluster where zfs_serial like '%{}%'
                    """.format(asn)
            print q
            zfs_serial = self.db.getRaw(q)[0][0]
            print zfs_serial
            q1 = """ UPDATE live.live_zfs_SNAPSHOTS
             SET asn ='{}' where asn = '{}'""".format(zfs_serial, asn)
            print q1
            self.db.queryExec(q1)

    def main(self):
        print 'total zfs count :', len(self.zfs_list)
        for zfs in self.zfs_list:
            print zfs
            zfs_pools(zfs).main()
        self.set_zfs_serial()


if __name__ == '__main__':
    # Manager().main()
    cnt =1
    Manager().main()
    #while True:
    #    Manager().main()
    #    print '-'*50
    #    print datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    #    print 'CNT :',cnt
    #    print '-'*50
    #    time.sleep(60*60)
    #    cnt = cnt+1