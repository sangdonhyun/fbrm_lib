str="""impact	character varying(200)
code	character varying(200)
uuid	character varying(50)
url	character varying(200)
description	character varying(200)
phoned_home	character varying(2000)
href	character varying(50)
diagnosed	character varying(200)
action	character varying(50)
type	character varying(200)
response	character varying(50)
severity	character varying(200)
"""
for line in str.splitlines():
    tmp= line.split()
    cnt= len(tmp)
    if cnt ==3:
        print "\"{}\" {} {} COLLATE pg_catalog.\"default\",".format(tmp[0],tmp[1],tmp[2])
    if cnt == 2:
        print "\"{}\" {},".format(tmp[0],tmp[1])
