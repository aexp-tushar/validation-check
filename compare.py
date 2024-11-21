import requests
import json
import os
with open('values.txt') as f:
    values_list = f.read().splitlines()
with open('cdaas.txt') as f:
    cdaas_list = f.read().splitlines()
cdaas_lst = []
for cd in cdaas_list:
    cdaas = cd.split(',')
    cdaas_lst.append(cdaas)
service_list = ['ESaaS','Kafka','kafka','Redis','Gridgain','AeroCache','CDaaS']
r = requests.request("GET",'http://lpdosput50093.phx.aexp.com:443/xPaaS_Inventory.json')
hosts={}
for service in service_list:
    hosts[service] = {}
for server_val in r.json():
    if  server_val.get('Host') in values_list and server_val.get("Nemo") ==  "N":
        for service in service_list:
            if service == server_val.get('Service'):
                lst = []
                lst.append(server_val.get('Role'))
                lst.append(server_val.get('ENV'))
                hosts[service][server_val.get('Host')] = lst
for cdaas_host in cdaas_lst:
    if cdaas_host[0] in values_list:
        hosts['CDaaS'][cdaas_host[0]] = cdaas_host
e3_lst = ["E3-IPC2","E3-IPC1","E3"]
for server in hosts.keys():
    if len(hosts[server])!= 0:
        for host,lst in hosts[server].items():
            if lst[1] in e3_lst:
                with open('E3_host_'+server, 'w+') as f:
                    for items in hosts[server]:
                        f.write('%s\n' %items)
                f.close()
            else: 
                with open('host_'+server, 'w+') as f:
                    for items in hosts[server]:
                        f.write('%s\n' %items) 
                
                f.close()
os.system("scp -r  E3_host_*  tbhat21@lppospwa40329.phx.aexp.com:/adshome/tbhat21/")
# for server in hosts.keys():
#     if len(hosts[server])!= 0:
        