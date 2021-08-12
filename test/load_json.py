import json
str="""{"version":
{"href": "/api/system/v1/version",
"nodename": "ZFS-VM",
"mkt_product": "Oracle ZFS Storage VirtualBox",
"product": "Sun Storage 7000",
"version": "2013.06.05.8.28,1-1.3",
"install_time": "Thu Nov 15 2018 23:10:39 GMT+0000 (UTC)",
"update_time": "Sat Apr 17 2021 15:52:14 GMT+0000 (UTC)",
"boot_time": "Wed Aug 04 2021 08:11:14 GMT+0000 (UTC)",
"asn": "df0c6049-dfae-4022-8320-edc1b00b8d8c",
"csn": "unknown",
"part": "Oracle 000-0000",
"urn": "urn:uuid:11da4018-a79e-11dd-a2a2-080020a9ed93",
"navname": "aksh 1.0",
"navagent": "aksh",
"http": "Apache/2.4.46 (Unix)",
"ssl": "OpenSSL 1.0.2u-fips  20 Dec 2019",
"ak_version": "ak/SUNW,ankimo@2013.06.05.8.28,1-1.3",
"ak_release": "OS8.8.28",
"os_version": "SunOS 5.11 11.4.28.82.3 64-bit",
"bios_version": "innotek GmbH (BIOS)VirtualBox (BIOS)12.01.2006",
"sp_version": "-"
}}"""

json_data= json.loads(str)

print type(json_data)