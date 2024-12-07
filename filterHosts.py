import requests
import json
import os
import os.path
print("Enter your ADS username: ")
ads = input()
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
                lst.append(server_val.get('Host'))
                lst.append(server_val.get('Role'))
                lst.append(server_val.get('ENV'))
                hosts[service][server_val.get('Host')] = lst
for cdaas_host in cdaas_lst:
    if cdaas_host[0] in values_list:
        hosts['CDaaS'][cdaas_host[0]] = cdaas_host
e3_lst = ["lpp","lgp","lep","lmp"]
e1_e2_lst = ["lpd","lpq"]

for service in hosts.keys():
    if len(hosts[service]) != 0:
        e3_host_lst = []
        host_lst = []
        for host_val in hosts[service].keys():
            if host_val[0:3] in e3_lst:
                e3_host_lst.append(host_val)
            elif host_val[0:3] in e1_e2_lst:
                host_lst.append(host_val)
        if len(e3_host_lst) !=0:
            with open('E3_host_'+service, 'w+') as file:
                for val in e3_host_lst:
                    file.write('%s\n' %val)
            file.close()
        if len(host_lst) != 0:
            with open('host_'+service, 'w+') as file:
                for val in host_lst:
                    file.write('%s\n' %val)
            file.close()
os.system('''
            scp -r  E3_host_*  %(ads)s@lppospwa40329.phx.aexp.com:/opt/xpaas_nik/nsukan/validation-check/
          ''' % locals())
with open ('hosts.txt','w') as file:
    file.write(json.dumps(hosts))
os.system('''
            scp -r  hosts.txt  %(ads)s@lppospwa40329.phx.aexp.com:/opt/xpaas_nik/nsukan/validation-check/
          ''' % locals())
kafka = False
ccc = False
schreg = False
ksql = False
for service in hosts.keys():
    if len(hosts[service]) != 0:
        if service in  ["Kafka","kafka"]:
            for hval in hosts[service].items():
                if hval[1][1] == "kafka" or hval[1][1] == "broker" or hval[1][1] == "zookeeper":
                   kafka=True
                if hval[1][1] == "ccc" or hval[1][1] == "CCC":
                    ccc=True
                if hval[1][1] == "SchemaRegistry" or hval[1][1] == "schemaregistry":
                    schreg=True
                if hval[1][1] == "ksql" or hval[1][1] == "KSQL":
                    ksql = True
for service in hosts.keys():
    if len(hosts[service]) != 0:
        path = "host_"+service
        if os.path.exists(path):
            if service == "ESaaS":
                print("Validating ",service," hosts")
                os.system('''
                          ansible all -i host_ESaaS -u %(ads)s -m shell -a "systemctl status elasticsearch | grep 'Active'" -bk
                          ''' % locals())
            if service == "AeroCache":
               print("Validating ",service," hosts")
               os.system('''
                        ansible all -i host_AeroCache -u %(ads)s -m shell -a "systemctl status aerospike | grep 'Active'" -bk
                         ''' % locals())
            if service in ["Kafka","kafka"]:
                print("Validating ",service," hosts")
                if kafka:
                    print("Running kafka role validation")
                    os.system('''
                          ansible all -i host_kafka -u %(ads)s -m shell -a "systemctl status kafka | grep 'Active'" -bk
                          ''' % locals())
                if ccc:
                    print("Running ccc role validation")
                    os.system('''
                            ansible all -i host_kafka -u %(ads)s -m shell -a "systemctl status ccc | grep 'Active'" -bk
                              ''' % locals())
                if schreg:
                    print("Running SchemaRegistry role validation")    
                    os.system('''
                            ansible all -i host_kafka -u %(ads)s -m shell -a "systemctl status schemaregistry | grep 'Active'" -bk
                              ''' % locals())
                if ksql:
                    print("Running ksql role validation")  
                    os.system('''
                            ansible all -i host_kafka -u %(ads)s -m shell -a "systemctl status ksql | grep 'Active'" -bk
                              ''' % locals())