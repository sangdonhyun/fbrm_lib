import zfs_pools
import zfs_problem
import zfs_sysver
import time
import datetime
class zfs_sched():
    def __init__(self):
        self.flib = zfs_pools.Manager()
        self.event = zfs_problem.Manager()
        self.sysver = zfs_sysver.Manager()

    def main(self):
        cnt = 1
        while True:

            self.flib.main()

            self.event.main()

            if cnt % 10 == 0 :
                self.sysver.main()


            print '#'*50
            print '#' * 50
            print '#  60sec wati'
            print '#' * 50
            print '#' * 50
            print 'count :',cnt
            cnt  = cnt +1
            print datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            time.sleep(60*5)


if __name__=='__main__':
    zfs_sched().main()