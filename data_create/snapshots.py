str="""id	character varying(200)
name	character varying(100)
pool	character varying(50)
project	character varying(50)
numclones	numeric
creation	character varying(50)
share	character varying(50)
collection	character varying(50)
href	character varying(200)
space_unique	numeric
space_data	numeric
isauto	character varying(50)
shadowsnap	character varying(50)
canonical_name	character varying(200)
type	character varying(50)


"""
for line in str.splitlines():
    tmp= line.split()
    cnt= len(tmp)
    if cnt ==3:
        print "\"{}\" {} {} COLLATE pg_catalog.\"default\",".format(tmp[0],tmp[1],tmp[2])
    if cnt == 2:
        print "\"{}\" {},".format(tmp[0],tmp[1])
