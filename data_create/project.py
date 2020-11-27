str="""default_volblocksize	numeric
readlimit	numeric
logbias	character varying(50)
shareobjectstore	character varying(50)
nodestroy	character varying(50)
href	character varying(200)
compression	character varying(50)
sharetftp	character varying(50)
encryption	character varying(50)
copies	character varying(50)
aclinherit	character varying(50)
compressratio	numeric
source	
space_total	numeric
recordsize	numeric
keychangedate	character varying(50)
space_available	numeric
space_unused_res	numeric
maxblocksize	numeric
atime	character varying(50)
default_user	character varying(50)
space_unused_res_shares	numeric
name	numeric
default_group	numeric
sharesftp	numeric
rstchown	numeric
sharesmb	numeric
defaultreadlimit	numeric
defaultgroupquota	numeric
creation	character varying(50)
sharenfs	character varying(50)
migration	character varying(50)
default_permissions	character varying(4)
mountpoint	character varying(200)
space_data	numeric
id	character varying(200)
defaultuserquota	numeric
default_sparse	character varying(50)
aclmode	character varying(50)
dedup	character varying(50)
snaplabel	character varying(50)
shareftp	character varying(50)
readonly	character varying(50)
default_volsize	numeric
secondarycache	character varying(50)
space_snapshots	numeric
quota	numeric
exported	character varying(50)
vscan	character varying(50)
reservation	numeric
keystatus	character varying(50)
pool	character varying(50)
writelimit	numeric
checksum	character varying(50)
canonical_name	character varying(200)
snapdir	character varying(50)
defaultwritelimit	numeric
sharedav	character varying(50)
nbmand	character varying(50)
"""
for line in str.splitlines():
    tmp= line.split()
    cnt= len(tmp)
    if cnt ==3:
        print "\"{}\" {} {} COLLATE pg_catalog.\"default\",".format(tmp[0],tmp[1],tmp[2])
    if cnt == 2:
        print "\"{}\" {},".format(tmp[0],tmp[1])
