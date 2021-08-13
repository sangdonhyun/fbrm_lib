# -*-coding:utf-8-*-
import os
import sys
import json
import ConfigParser
import fbrm_dbms
import datetime
import time


class zfs_problem():
    def __init__(self, zfs):
        self.zfs = zfs
        self.cfg = self.get_cfg()
        self.common_cmd = self.get_common_cmd()
        self.set_path()
        self.db = fbrm_dbms.fbrm_db()
        self.today = datetime.datetime.now()
        self.to_day_d = self.today.strftime('%Y-%m-%d')
        self.zfs_ip = self.zfs['ip']
        self.zfs_name = self.zfs['name']
        self.fbrm_datetime = self.today.strftime('%Y-%m-%d %H:%M:%S')

    def set_path(self):
        curl_path = self.cfg.get('common', 'curl_path')
        path = os.environ['PATH']
        os.environ['PATH'] = '{};{}'.format(curl_path, path)

    def get_common_cmd(self):
        cmd = "curl --user {}:{} -k -L https://{}:{}".format(self.zfs['user'], self.zfs['passwd'], self.zfs['ip'],
                                                             self.zfs['port'])
        self.fwrite(cmd)
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
        with open('chassis.txt', wbit) as f:
            f.write(msg + '\n')

    def set_colon(self, dict):
        for key in dict.keys():
            val = dict[key]
            val = val.replace('\'', '`')
            val = val.replace('\"', '~')
            dict[key] = val
        return dict

    def get_sysver(self):
        url = '/api/system/v1/version'
        cmd = self.common_cmd + url
        print cmd
        ret = os.popen(cmd).read()
        # root = self.get_json(ret)
        root = json.loads(ret)
        zfs_info = root['version']
        return zfs_info['asn']

    def main(self):
        asn = self.get_sysver()
        problem_list = []
        url = '/api/hardware/v1/chassis'
        cmd = self.common_cmd + url
        print cmd
        ret = os.popen(cmd).read()
        # root = self.get_json(ret)
        root = json.loads(ret)
        chassis_list = []
        for chassis in root['chassis']:
            href = chassis['href']
            chassis_list.append(href)
        hardware_list = []
        cpu_list = []
        disk_list = []
        for url in chassis_list:
            cmd = self.common_cmd + url
            print cmd
            ret = os.popen(cmd).read()
            root = self.get_json(ret)
            chassis = root['chassis']
            chassis_name = os.path.basename(url)
            print chassis_name
            print asn
            print chassis['name']
            print chassis['model']
            print chassis['type']
            print chassis['serial']
            print chassis['manufacturer']
            # ['faulted', 'name', 'cpu', 'href', 'model', 'disk', 'type', 'serial', 'manufacturer']
            dict = {}
            print chassis.keys()
            dict['asn'] = asn.encode('utf-8')
            dict['chassis_name'] = chassis_name.encode('utf-8')
            dict['name'] = chassis['name'].encode('utf-8')
            dict['model'] = chassis['model'].encode('utf-8')
            dict['type'] = chassis['type'].encode('utf-8')
            dict['serial'] = chassis['serial'].encode('utf-8')
            dict['manufacturer'] = chassis['manufacturer'].encode('utf-8')
            dict['fbrm_datetime'] = self.fbrm_datetime
            for key in dict.keys():
                val = dict[key]
                dict[key] = val.encode('utf-8')
            hardware_list.append(dict)
            print chassis.keys()
            for cpus in chassis['cpu']:
                print cpus.keys()
                # ['faulted', 'name', 'cpu', 'href', 'model', 'disk', 'type', 'serial', 'manufacturer']
                print cpus.values()
                # ['faulted', 'label', 'href', 'cores', 'model', 'speed', 'present', 'manufacturer']
                cpus['asn'] = asn.encode('utf-8')
                cpus['chassis_name'] = chassis_name.encode('utf-8')
                cpus['name'] = chassis['name'].encode('utf-8')
                cpus['cpu_speed'] = str(cpus['speed']).encode('utf-8')
                cpus['cores'] = str(cpus['cores']).encode('utf-8')
                cpus['label'] = str(cpus['label']).encode('utf-8')
                cpus['href'] = str(cpus['href']).encode('utf-8')
                cpus['model'] = str(cpus['model']).encode('utf-8')
                cpus['manufacturer'] = str(cpus['manufacturer']).encode('utf-8')
                del (cpus['speed'])
                cpus['fbrm_datetime'] = self.fbrm_datetime
                cpu_list.append(cpus)

            for disk in chassis['disk']:
                print disk.keys()
                print disk.values()
                if 'use' in disk.keys():
                    disk['disk_use'] = disk['use']
                    del (disk['use'])
                else:
                    disk['disk_use'] = ''
                disk['asn'] = asn.encode('utf-8')
                disk['chassis_name'] = chassis_name.encode('utf-8')
                disk['name'] = chassis['name'].encode('utf-8')
                disk['size'] = str(disk['size']).encode('utf-8')

                disk['fbrm_datetime'] = self.fbrm_datetime
                if 'readytoremove' in disk.keys():
                    del(disk['readytoremove'])

                for key in disk.keys():
                    if type(disk[key]) == type(u'aa'):
                        disk[key] = disk[key].encode('utf-8')
                disk_list.append(disk)
        query = "delete from master.master_zfs_hardware where asn = '{}'".format(asn)
        self.db.queryExec(query)
        db_name = 'master.master_zfs_hardware'
        self.db.dbInsertList(hardware_list, db_name)
        query = "delete from master.master_zfs_hardware_cpus where asn = '{}'".format(asn)
        self.db.queryExec(query)
        db_name = 'master.master_zfs_hardware_cpus'
        self.db.dbInsertList(cpu_list, db_name)
        query = "delete from master.master_zfs_hardware_disks where asn = '{}'".format(asn)
        self.db.queryExec(query)
        db_name = 'master.master_zfs_hardware_disks'

        self.db.dbInsertList(disk_list, db_name)
        # self.db.dbInsertList(problem_list,'event.evt_zfs_problem')


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
            zfs_problem(zfs).main()


if __name__ == '__main__':
    Manager().main()
    # while True:
    #     try:
    #         Manager().main()
    #     except:
    #         pass
    #     time.sleep(60)