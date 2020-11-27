import datetime
utc="Thu Nov 15 2018 23:10:39 GMT+0000 (UTC)"
utc_time = datetime.datetime.strptime(utc,"%a %b %d %Y %H:%M:%S GMT+0000 (UTC)")
ks_time = utc_time + datetime.timedelta(hours=9)

print utc_time
print ks_time.strftime('%Y-%m-%d %H:%M:%S')
