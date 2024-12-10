import requests
import json
import os
import os.path
from getpass import getpass
import glob
print("Enter your ADS username: ")
ads = input()
passwd = getpass('Enter ADS password: ')
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
                lst.append(server_val.get('AimName'))
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
e3_files = "E3_host_*"
if glob.glob(e3_files):
    print("#########################################Transferring Host files  to E3 Jump Server , please run script post validating here ##################################################")
    os.system('''
                sshpass -p%(passwd)s scp -r  E3_host_*  %(ads)s@lppospwa40329.phx.aexp.com:/opt/xpaas_nik/nsukan/validation-check
            ''' % locals())
    with open ('hosts.txt','w') as file:
        file.write(json.dumps(hosts))
    os.system('''
                sshpass -p%(passwd)s scp -r  hosts.txt values.txt  %(ads)s@lppospwa40329.phx.aexp.com:/opt/xpaas_nik/nsukan/validation-check
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
rc = False
abs = False
asm = False
gmnt = False 
for grhost in hosts['Gridgain'].keys():
    if hosts['Gridgain'][grhost][3] == "Registered Card":
        rc = True
    if hosts['Gridgain'][grhost][3] == "Global Treasury Securitization Platform":
        abs = True
    if hosts['Gridgain'][grhost][3] == "ES - SUBMISSION MONITOR - AESC - NA":
        asm = True
    if hosts['Gridgain'][grhost][3] == "ES - MERCHANT PAYMENT ENGINE":
        gmnt = True
for service in hosts.keys():
    if len(hosts[service]) != 0:
        path = "host_"+service
        if os.path.exists(path):
            if service == "CDaaS":
                print("Validating ",service," hosts")
                os.system('''
                          sshpass -p%(passwd)s  ansible all -i host_CDaaS -u  %(ads)s -m shell -a "echo $'\nNginx status\n' && systemctl status nginx | grep -i 'Active' ;  echo $'\nmnt-cdaas.mount status\n'  &&  systemctl status mnt-cdaas.mount | grep -i 'Active'  ; echo $'\nmnt-cdaas.automount status\n' &&  systemctl status mnt-cdaas.automount | grep -i 'Active'  ; echo $'\nnode-exporter status\n' && systemctl status node-exporter | grep -i 'Active'  ; echo $'\nsplunk status\n'  &&  systemctl status splunk | grep -i 'Active'  ; echo $'\necp status\n' && service ecp status | grep -i 'Active'  ; echo $'\nDeployer  status\n'  &&  systemctl status deployer | grep -i 'Active'" -bk
                          ''' % locals())
            if service == "ESaaS":
                print("Validating ",service," hosts")
                os.system('''
                          sshpass -p%(passwd)s ansible all -i host_ESaaS -u %(ads)s   -m shell -a "systemctl status elasticsearch | grep -i 'Active'" -bk
                          ''' % locals())
            if service == "AeroCache":
               print("Validating ",service," hosts")
               os.system('''
                        sshpass -p%(passwd)s ansible all -i host_AeroCache -u %(ads)s  -m shell -a "systemctl status aerospike | grep -i 'Active'" -bk
                         ''' % locals())
            if service in ["Kafka","kafka"]:
                print("Validating ",service," hosts")
                if kafka:
                    print("Running kafka role validation")
                    os.system('''
                          sshpass -p%(passwd)s ansible all -i host_kafka -u %(ads)s  -m shell -a "systemctl status kafka | grep -i 'Active'" -bk
                          ''' % locals())
                if ccc:
                    print("Running ccc role validation")
                    os.system('''
                            sshpass -p%(passwd)s ansible all -i host_kafka -u %(ads)s  -m shell -a "systemctl status ccc | grep -i 'Active'" -bk
                              ''' % locals())
                if schreg:
                    print("Running SchemaRegistry role validation")    
                    os.system('''
                            sshpass -p%(passwd)s ansible all -i host_kafka -u %(ads)s  -m shell -a "systemctl status schemaregistry | grep -i 'Active'" -bk
                              ''' % locals())
                if ksql:
                    print("Running ksql role validation")  
                    os.system('''
                            sshpass -p%(passwd)s ansible all -i host_kafka -u %(ads)s  -m shell -a "systemctl status ksql | grep -i 'Active'" -bk
                              ''' % locals())
            if service == 'Gridgain':
                print("Validating ",service," hosts")
                if asm:
                    print("Running Gridgain ASM validation")
                    os.system('''
                          sshpass -p%(passwd)s ansible all -i host_Gridgain -u %(ads)s  -m shell -a "echo $'\nWebconsole status\n' && systemctl status webconsole | grep -i 'Active'; echo $'\nGridgain-risk status\n' && systemctl status gridgain-risk | grep -i 'Active';echo $'\nGridgain-ram status\n' && systemctl status gridgain-ram | grep -i 'Active'" -bk
                          ''' % locals())
                if gmnt:
                    print("Running Gridgain GMNT validation")
                    os.system('''
                            sshpass -p%(passwd)s ansible all -i host_Gridgain -u %(ads)s  -m shell -a "echo $'\nGridgain-cluster1.service status\n' && systemctl status gridgain-cluster1.service | grep -i 'Active'; echo $'\nGridgain-cluster2.service status\n' && systemctl status gridgain-cluster2.service | grep -i 'Active';echo $'\nWebconsole status\n' && systemctl status webconsole | grep -i 'Active'; echo $'\nWebagent status\n' && systemctl status webagent | grep -i 'Active';echo $'\nGridgain-cluster3.service status\n' && systemctl status gridgain-cluster3.service | grep -i 'Active';echo $'\nGridgain-cluster4.service status\n' && systemctl status gridgain-cluster4.service | grep -i 'Active'" -bk
                              ''' % locals())
                if abs:
                    print("Running Gridgain ABS validation")    
                    os.system('''
                            sshpass -p%(passwd)s ansible all -i host_Gridgain -u %(ads)s  -m shell -a "systemctl status gridgain | grep -i 'Active'" -bk
                              ''' % locals())
                if rc:
                    print("Running Gridgain RC validation")  
                    os.system('''
                            sshpass -p%(passwd)s ansible all -i host_Gridgain -u %(ads)s  -m shell -a "echo $'\nGridgain-compute.service status\n' && systemctl status gridgain-compute.service | grep -i 'Active'; echo $'\nGridgain-client.service status\n' && systemctl status gridgain-client.service | grep -i 'Active';echo $'\nOneagent.service status\n' && systemctl status oneagent.service | grep -i 'Active'" -bk
                              ''' % locals())
print("Validation Done ..... Deleting host files.......")
os.system('''
            rm -rf E3_*  host* 
          ''')