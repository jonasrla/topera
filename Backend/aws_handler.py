import boto.ec2
import boto.ec2.connection
import csv
import time
import paramiko
from scp import SCPClient
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("file", help="Put the name of the .zip if extention file containing the complete webserver\nIt must contain:\n1. topera.py\n2. data/\n3. database/\n4. static/\n5. templates/")
file_name = parser.parse_args().file

f = open('credentials.csv','r')
reader = csv.reader(f,delimiter=',')
reader.next()
key = reader.next()
f.close()
connection = boto.ec2.connect_to_region('us-east-1', aws_access_key_id=key[1], aws_secret_access_key=key[2])
sec_group = None

try:
    print "Trying to create security group"
    sec_group = connection.create_security_group('csc326-group30','group for users of the search engine Topera')


    connection.authorize_security_group(group_name='csc326-group30', ip_protocol='ICMP', from_port=-1, to_port=-1, cidr_ip='0.0.0.0/0')
    connection.authorize_security_group(group_name='csc326-group30', ip_protocol='TCP', from_port=22, to_port=22, cidr_ip='0.0.0.0/0')
    connection.authorize_security_group(group_name='csc326-group30', ip_protocol='TCP', from_port=80, to_port=80, cidr_ip='0.0.0.0/0')
    print "Secutiry Group Created. Name: csc326-group30"
except boto.exception.EC2ResponseError:
    sec_group = 'csc326-group30'
    print "The Security Group is Already Created"

print "Creating instance"
res = connection.run_instances('ami-8caa1ce4', key_name="topera", security_groups=["csc326-group30"])
ins = res.instances[0]
while ins.state != unicode('running'):
    print "."
    time.sleep(1)
    ins.update()
ip = ins.ip_address
print "Creation Successful. IP: " + ip

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

while True:
    print "Trying to connect..."
    time.sleep(5)
    try:
        client.connect(ip,username="ubuntu",key_filename="topera.pem", timeout=20.0)
        print "Connection Successful"
        break
    except Exception:
        print "Connection Failed"
        print "Trying againg" 
        time.sleep(5)

print "Setting up the machine"
commands = ['sudo apt-get update','sudo apt-get install python-pip python-dev build-essential', 'sudo pip install --upgrade pip', 'sudo pip install --upgrade virtualenv', 'sudo pip install bottle', 'sudo pip install --upgrade oauth2client', 'sudo pip install --upgrade google-api-python-client', 'sudo pip install beaker', 'sudo pip install peewee','sudo apt-get install unzip']
for n, com in enumerate(commands):
    stdin, stdout, stderr = client.exec_command(com)
    if n == 1:
        # time.sleep(3)
        stdin.write('y\n')
        time.sleep(100)
    else:
        time.sleep(20)
    print "executed '"+com+"'"


if __name__=="__main__":
    scp = SCPClient(client.get_transport())
    print "Uploading Webserver"
    scp.put(file_name)
    time.sleep(5)
    stdin, stdout, stderr = client.exec_command("unzip "+file_name)
    print "Setting up server"
    time.sleep(10)
    stdin, stdout, stderr = client.exec_command("cd "+file_name[:-4])
    time.sleep(1)
    print "Executing"
    stdin, stdout, stderr = client.exec_command("screen -d -m sudo python server.py")
    time.sleep(2)
    # print stdout.next()

    print "connection %s" % ("ok" if connection else "failed")
    print "key pair %s" % ("ok" if key else "failed")
    print "security group %s" % ("ok" if sec_group else "failed")
    print "reservation %s" % ("ok" if res else "failed")
    print "instance %s" % ("ok" if ins else "failed")
    print "ip %s" % ("ok" if ip else "failed")
    print "\n"
    print "Website IP: "+ip
