#!flask/bin/python
from flask import Flask, jsonify, request
import mysql.connector as mariadb
import os
import time

app = Flask(__name__)

tasks = []

def check_flavor(flavor):
    current_vcpus = 0
    current_memory = 0
    mariadb_connection = mariadb.connect(host="192.168.126.28", user='nova', password='9xcs@nova', database='nova')
    cursor = mariadb_connection.cursor()
    cursor.execute("SELECT name,memory_mb,vcpus FROM instance_types")
    for name,memory_mb,vcpus in cursor:
       if(name == flavor):
          current_vcpus = vcpus
          current_memory = memory_mb  
    mariadb_connection.close()
    return current_vcpus,current_memory

def create_instance(vcpus_req,mem_req):
   min_vcpus_used = 0.00
   hostname = " "
   hosts = []
   C = []
   R = []
   selected_hosts =[]
   mariadb_connection = mariadb.connect(host="192.168.126.28", user='nova', password='9xcs@nova', database='nova')
   cursor = mariadb_connection.cursor()
   cursor1 = mariadb_connection.cursor()

   cursor1.execute("SELECT host,disabled FROM services")
   for host,disabled in cursor1:
      if(disabled == 1):
         hosts.append(host)

   cursor.execute("SELECT memory_mb,free_ram_mb,vcpus,vcpus_used,host FROM compute_nodes")
   for memory_mb,free_ram_mb,vcpus,vcpus_used,host in cursor:
      bi = False
      for host1 in hosts:
         if (host1 == host):
            bi = True
            
#      C = float(float(vcpus - vcpus_used)/float(vcpus) * 100.00)
#      R = float(float(free_ram_mb)/float(memory_mb) * 100.00)
#      print("RAM Used Percent = {} Hostname {}").format((C+R)/2,host)
#     print len(selected_hosts)
      if(bi==False and mem_req <= free_ram_mb and vcpus_req <= (vcpus-vcpus_used)):
         selected_hosts.append(host)
         C.append(float(float(vcpus - vcpus_used)/float(vcpus) * 100.00))
         R.append(float(float(free_ram_mb)/float(memory_mb) * 100.00))
      
   if(len(selected_hosts)!=0):
      count = 0
      for host2 in selected_hosts:
         if((C[count]+R[count])/2 > min_vcpus_used):
            min_vcpus_used = (C[count]+R[count])/2
            hostname = host2            
#           print("Used Percent = {} Hostname {}").format((C[count]+R[count])/2,hostname)
         count = count + 1
      mariadb_connection.close()
      return hostname
   else:
      mariadb_connection.close()
      return 'NULL'

#   mariadb_connection.close()
#   return hostname

@app.route('/config', methods=['POST'])
def create_task():
    vcpus_req = 0
    mem_req = 0
    if not request.json:
        abort(400)
    task = {
        'flavor': request.json['flavor'],
        'image': request.json['image'],
        'secgroup': request.json['secgroup'],
        'keyname': request.json['keyname'],
        'nic': request.json['nic'],
        'name': request.json['name']
    }
    tasks=[task]
    vcpus_req,mem_req = check_flavor(request.json['flavor'])
    selected_host=create_instance(vcpus_req,mem_req)
    if(selected_host!='NULL'):
       os.system("source ~/provider-openrc.sh")
       command = "nova boot --flavor "+request.json['flavor']+" --image "+request.json['image']+" --security-groups "+request.json['secgroup']+" --key-name "+request.json['keyname']+" --nic "+request.json['nic']+" "+request.json['name']+" --availability-zone nova:"+selected_host
       os.system(command)
    else:
       os.system("ipmitool -I lanplus -H gcloud-compute10.bmc.lo -U gcloud -P gcloud@GSDC chassis power on")
       time.sleep(210)
       print"No valid host found....!!"
#    vcpus_req,mem_req = check_flavor(request.json['flavor'])
    return jsonify({'task': task}), 201

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)

