import requests
import json
with open('values.txt') as f:
    values_list = f.read().splitlines()
with open('cdaas.txt') as f:
    cdaas_list = f.read().splitlines()
service_list = ['ESaaS','Kafka','kafka','Redis','Gridgain','AeroCache','CDaaS']
r = requests.request("GET",'http://lpdosput50093.phx.aexp.com:443/xPaaS_Inventory.json')
hosts={}
for service in service_list:
    hosts[service] = {}
for server_val in r.json():
    if  server_val.get('Host') in values_list and server_val.get("Nemo") ==  "N":
        for service in service_list:
            if service == server_val.get('Service'):
                hosts[service][server_val.get('Host')] = server_val.get('Role')
for cdaas in cdaas_list:
    if cdaas in values_list:
        hosts['CDaaS'][cdaas] = cdaas
for server in hosts.keys():
    if len(hosts[server])!= 0:
        with open('hosts_'+server, 'w+') as f:
            for items in hosts[server]:
                f.write('%s\n' %items) 
            print(server+" Host file ready")
        f.close()