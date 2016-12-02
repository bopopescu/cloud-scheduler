#!/usr/bin/python
import mysql.connector as mariadb
import os
import time

min_vcpus_used = 0.00
hostname = " "
hosts = []
C = 0.00
R = 0.00
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
   C = float(float(vcpus - vcpus_used)/float(vcpus) * 100.00)
   R = float(float(free_ram_mb)/float(memory_mb) * 100.00)
   print("RAM Used Percent = {} Hostname {}").format((C+R)/2,host)
   if ((C+R)/2 > min_vcpus_used and bi==False):
       min_vcpus_used = (C+R)/2
       hostname = host
#print("Min VCPUS Hostname = {}").format(hostname)
   
#       print("RAM Used = {}").format(memory_mb_used)
#       print("DISK Used = {}").format(local_gb_used)

#cursor1.execute("SELECT name,deleted_at FROM instance_types")
#for name,deleted_at in cursor1:
#  if (deleted_at == None):
#      print("Flavor Name = {}").format(name)
#      print("Flavor Deleted = {}").format(deleted_at)

ostname = "gcloud-compute02.sdfarm.kr"
os.system("source ~/provider-openrc.sh")
command = "nova boot --flavor m1.xlarge  --image ONOS-Installed-Image --security-groups default --key-name new-key --nic net-id=69c93c16-0cd4-4b3c-a249-2d0d4513fa42 ONOS-instance01 --availability-zone nova:"+hostname
os.system(command)



mariadb_connection.close()
