str="""status	character varying(50)
profile	character varying(50)
name	character varying(200)
encryption	character varying(50)
owner	character varying(50)
	
href	character varying(200)
peer	character varying(200)
asn	character varying(200)
	
u_available	numeric
u_usage_snapshots	numeric
u_usage_metasize	numeric
u_used	numeric
u_compression	numeric
u_usage_child_reservation	numeric
u_dedupsize	numeric
u_usage_reservation	numeric
u_free	numeric
u_usage_data	numeric
u_usage_replication	numeric
u_dedupratio	numeric
u_usage_metaused	numeric
u_total	numeric
u_usage_total	numeric
"""
for line in str.splitlines():
    tmp= line.split()
    cnt= len(tmp)
    if cnt ==3:
        print "\"{}\" {} {} COLLATE pg_catalog.\"default\",".format(tmp[0],tmp[1],tmp[2])
    if cnt == 2:
        print "\"{}\" {},".format(tmp[0],tmp[1])
