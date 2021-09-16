# -*-coding:utf-8-*-
import os
import sys
import json
import ConfigParser
import fbrm_dbms
import datetime
import zfs_chassis


class zfs_sys():
    def __init__(self, zfs):
        self.zfs = zfs
        self.cfg = self.get_cfg()
        self.common_cmd = self.get_common_cmd()
        self.set_path()
        self.db = fbrm_dbms.fbrm_db()
        self.today = datetime.datetime.now()
        self.fbrm_datetime = self.today.strftime('%Y-%m-%d %H:%M:%S')


    def set_path(self):
        curl_path = self.cfg.get('common', 'curl_path')
        path = os.environ['PATH']
        os.environ['PATH'] = '{};{}'.format(curl_path, path)

    def get_common_cmd(self):
        cmd = "curl --user {}:{} -k -L https://{}:{}".format(self.zfs['user'], self.zfs['passwd'], self.zfs['ip'],
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

    def fwrite(self, msg, wbit='a'):
        with open('{}_sysver.txt'.format(self.zfs['ip']), wbit) as f:
            f.write(msg + '\n')

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

    def get_cluster(self, asn, zfs_name):
        print '#' * 50
        print 'system asn'
        print '#' * 50
        print 'asn :', asn
        pool_cmd = '/api/hardware/v1/cluster'
        cmd = self.common_cmd + pool_cmd
        print cmd
        ret = os.popen(cmd).read()
        print ret
        cluster_json = self.get_json(ret)

        cluster_list = []
        resource_list = []
        cluster_dict = {}


        for cluster in cluster_json['cluster']:
            cluster_dict['asn'] = asn
            cluster_dict['cluster_name'] = zfs_name
            cluster_dict['node_name'] = self.node_name
            cluster_dict['fbrm_date'] = self.fbrm_datetime
            print '-' * 50
            print cluster
            print cluster_json['cluster'][cluster]
            if not cluster == 'resources':
                val = cluster_json['cluster'][cluster]

                if "'" in val:
                    val = val.replace("'", "`")
                if "[" in val:
                    val = ','.join(list(val))
                cluster_dict[cluster] = str(val)
            else:
                resource_dict = {}
                resouces = cluster_json['cluster'][cluster]
                for resource in resouces:
                    res_dict = {}
                    res_dict['asn'] = asn
                    for key in resource.keys():
                        val = resource[key]
                        if "'" in val:
                            val = val.replace("'", "`")
                        if type(val) == type([]):
                            val = ','.join(val)
                        res_dict[key] = val
                        res_dict['fbrm_date'] = self.fbrm_datetime
                    resource_list.append(self.set_utf(res_dict))

        asn = cluster_dict['asn'].encode("utf-8")
        peer_asn = cluster_dict['peer_asn']

        print '-'*50
        if not peer_asn =="":
            zfs_serial=''.join(sorted([asn,peer_asn]))
        else:
            zfs_serial = asn
        cluster_dict['zfs_serial'] = zfs_serial
        cluster_dict['cluster_name'] = self.cluster_name
        print 'zfs_serial :',zfs_serial
        print cluster_dict
        asn_list = self.get_asn_list()
        serial_list = self.get_mst_cluter()
        mst_cluster_list=[]
        print '*'*50
        print zfs_serial
        print not zfs_serial in serial_list

        if not zfs_serial in serial_list:
            mst_cluster=dict()
            mst_cluster['zfs_serial'] = zfs_serial.encode("utf-8")
            mst_cluster['cluster_name'] = self.cluster_name
            mst_cluster['reg_usr'] = 'SYS'
            mst_cluster_list.append(mst_cluster)
            """
            5c5bd1d2-402c-65ed-f1a0-fa54bccf3783b4e84805-d835-4eef-d1a3-fc18b9eebf67	PEDW_BOX_#3	SYS	20210524010842
            3e9e38da-8972-4768-99eb-dae2959e85ec7430f3fb-c8bf-ec76-d8e1-9a2019310032	PEDW_BOX_#1	SYS	20210524010842
            1be8103e-c0cb-40bc-c5f1-b57e93c26ada32c442b2-5779-c93b-9301-dc123ff292bb	PEDW_BOX_#2	SYS	20210524010842
            2c155bd1-176b-4480-8325-f037b6774ccca3135a47-1d33-49f7-b1c6-9aec97ffd88f	PCOR_BOX_#2	SYS	20210524010842
            332fa851-8c38-4f62-ba49-ea035894b306af2fa30c-5bc0-422a-89b2-987da66c2af5	PCOR_BOX_#1	SYS	20210524010842
            """
            serial_list.append(zfs_serial.encode("utf-8"))

        print asn,type(asn),asn_list,not asn in asn_list
        if not asn in asn_list:
            cluster_list.append(self.set_utf(cluster_dict))



        db_name = 'master.master_zfs_cluster'
        print cluster_list
        self.db.dbInsertList(cluster_list, db_name)

        sql="DELETE FROM master.master_zfs_cluster_resouces mzcr  WHERE asn ='{}'".format(asn)
        self.db.queryExec(sql)
        db_name = 'master.master_zfs_cluster_resouces'
        self.db.dbInsertList(resource_list, db_name)
        db_name = 'master.mst_cluster'
        print mst_cluster_list
        self.db.dbInsertList(mst_cluster_list, db_name)

    def get_sysver(self, zfs_info):
        return zfs_info['asn']

    def set_utf(self, info):
        for key in info.keys():
            if isinstance(info[key], unicode):
                info[key] = info[key].encode("utf-8")
        return info

    def get_cluster_nm(self):
        query = "SELECT zfs_cluster FROM master.master_zfs_info where asn = '{}'".format(self.asn)
        cluster_name = ''
        try:
            cluster_name = self.db.getRaw(query)[0][0]
        except:
            pass
        if cluster_name =='':
            query = """SELECT peer_hostname ,node_name FROM master.master_zfs_cluster WHERE zfs_serial LIKE '%{}%'""".format(
                self.asn)
            print query
            zfs = self.db.getRaw(query)
            print zfs
            cluster_name = ''
            for z in zfs:
                cluster_name = '_'.join(sorted(set(z)))
            print cluster_name

        return cluster_name

    def get_asn_list(self):
        query = "SELECT asn FROM master.master_zfs_cluster "
        asn_list = list()
        raws=self.db.getRaw(query)
        try:
            for asns in raws:
                asn = asns[0]

                if asn not in asn_list:
                    asn_list.append(asn)
        except:
            pass
        return asn_list

    def get_mst_cluter(self):
        query = "SELECT zfs_serial FROM master.mst_cluster "
        raws = self.db.getRaw(query)
        serial_list = list()
        for r in raws:
            serial_list.append(r[0])
        return serial_list


    def main(self):
        asn_list = self.get_asn_list()
        self.fwrite('-', 'w')
        zfs_list = []
        url = '/api/system/v1/version'
        cmd = self.common_cmd + url

        self.fwrite(cmd)
        ret = os.popen(cmd).read()
        print ret

        root = self.get_json(ret)

        zfs_info = root['version']
        zfs_info['zfs_name'] = self.zfs['name']
        zfs_info['zfs_ip'] = self.zfs['ip']
        zfs_info['fbrm_date'] = self.today.strftime('%Y-%m-%d %H:%M:%S')
        print '-'*40
        print '-'*40
        print zfs_info['asn'],asn_list,zfs_info['asn'] not in asn_list
        if zfs_info['asn'] not in asn_list:
            asn=zfs_info['asn']
            try:
                peer_asn=zfs_info['peer_asn']
            except:
                peer_asn = ''
            zfs_serial = ''.join(sorted([asn,peer_asn]))
            zfs_info['zfs_serial'] = zfs_serial
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
        print 'update_time :', update_time
        print 'update_time :', self.to_local_time(update_time)
        try:
            self.db.dbInsertList(zfs_list, 'master.master_zfs_info')
        except Exception as e:
            print 'error '
            print str(e)

        asn = zfs_info['asn']
        self.asn = asn
        self.cluster_name = self.get_cluster_nm()
        zfs_name = zfs_info['node_name']
        self.node_name = zfs_info['node_name']
        self.get_cluster(asn, zfs_name)
        print 'zfs_name :', zfs_name


class Manager():
    def __init__(self):
        self.zfs_list = self.get_zfs_list()

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

    def main(self):
        for zfs in self.zfs_list:
            zfs_sys(zfs).main()



if __name__ == '__main__':
    Manager().main()
    zfs_chassis.Manager().main()