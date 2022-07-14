
class zfs_register():

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