

str="""fbrm_date, ins_date_time, "name", id, pool, default_volblocksize, readlimit, logbias, shareobjectstore, nodestroy, href, compression, sharetftp, encryption, copies, aclinherit, compressratio, space_total, recordsize, keychangedate, space_available, space_unused_res, maxblocksize, atime, default_user, space_unused_res_shares, default_group, sharesftp, rstchown, sharesmb, defaultreadlimit, defaultgroupquota, creation, sharenfs, migration, default_permissions, mountpoint, space_data, defaultuserquota, default_sparse, aclmode, dedup, snaplabel, shareftp, readonly, default_volsize, secondarycache, space_snapshots, quota, exported, vscan, reservation, keystatus, writelimit, checksum, canonical_name, snapdir, defaultwritelimit, sharedav, nbmand, zfs_name, zfs_ip, "source", cluster_ip, asn, node_name, cluster_name"""

col_list=list()
for col in str.split(','):
    print (col)
    if '"' in col:
        col = col.replace('"','').strip()
    print(col)
    col_list.append(col)



print(col_list)