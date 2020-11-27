ret="""	zfs_name	character varying(50)	,
	zfs_ip	charactor varying(50)	,
	zfs_alias	charactor varying(50)	,
	ak_release	charactor varying(50)	,
	product	charactor varying(50)	,
	csn	charactor varying(50)	,
	http	charactor varying(50)	,
	nodename	charactor varying(50)	,
	mkt_product	charactor varying(200)	,
	urn	charactor varying(200)	,
	ak_version	charactor varying(200)	,
	update_time	charactor varying(200)	,
	ssl	charactor varying(200)	,
	navagent	charactor varying(50)	,
	href	charactor varying(50)	,
	os_version	charactor varying(200)	,
	boot_time	charactor varying(200)	,
	version	charactor varying(50)	,
	bios_version	charactor varying(200)	,
	part	charactor varying(50)	,
	install_time	charactor varying(200)	,
	sp_version	charactor varying(50)	,
	asn	charactor varying(50)	,
	navname	charactor varying(50)	"""

for line in ret.splitlines():
    tmp= line.split()
    print "\"{}\" {} {} COLLATE pg_catalog.\"default\",".format(tmp[0],tmp[1],tmp[2])