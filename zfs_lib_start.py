import zfs_pools
import zfs_problem
import zfs_sched
import datetime
import time
cnt=1
while True:
    try:
        zfs_pools.Manager().main()
        zfs_problem.Manager.main()
        zfs_sched.zfs_sched().main()
    except:
        pass

    print '#'*50
    print '#' * 50
    print '#' * 50
    print '#' * 50
    print datetime.datetime.now()
    print 'cnt :',cnt
    cnt = cnt+1
    time.sleep(60)
