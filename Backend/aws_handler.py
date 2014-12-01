import boto.ec2
import boto.ec2.connection
import csv
import time
import paramiko
from scp import SCPClient

f = open('credentials.csv','r')
reader = csv.reader(f,delimiter=',')
reader.next()
key = reader.next()
f.close()
connection = boto.ec2.connect_to_region('us-east-1', aws_access_key_id=key[1], aws_secret_access_key=key[2])
# key = connection.create_key_pair('topera')
# key.save(".")
sec_group = None
try:
    sec_group = connection.create_security_group('csc326-group30','group for users of the search engine Topera')


    connection.authorize_security_group(group_name='csc326-group30', ip_protocol='ICMP', from_port=-1, to_port=-1, cidr_ip='0.0.0.0/0')
    connection.authorize_security_group(group_name='csc326-group30', ip_protocol='TCP', from_port=22, to_port=22, cidr_ip='0.0.0.0/0')
    connection.authorize_security_group(group_name='csc326-group30', ip_protocol='TCP', from_port=80, to_port=80, cidr_ip='0.0.0.0/0')
except boto.exception.EC2ResponseError:
    sec_group = 'csc326-group30'
    print "Already exist"

res = connection.run_instances('ami-8caa1ce4', key_name="topera", security_groups=["csc326-group30"])
ins = res.instances[0]
while ins.state != unicode('running'):
    print "."
    time.sleep(1)
    ins.update()
ip = ins.ip_address
print ip

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

# raw_input("Wait for the machine then press any key\n")
print "Waiting for the machine. It will take about 10 minutes"
time.sleep(300)
print "5 minutes left"
time.sleep(300)
while True:
    print "Trying to connect..."
    try:
        client.connect(ip,username="ubuntu",key_filename="topera.pem", timeout=20.0)
        print "Connection Successful"
        break
    except Exception:
        print "Connection Failed"
        answer = raw_input("Try again?[y/n]\n")
        if answer.strip() in ["y","Y","yes"]:
            time.sleep(5)
            print "Trying againg" 
        else:
            break

commands = ['sudo apt-get update','sudo apt-get install python-pip python-dev build-essential', 'sudo pip install --upgrade pip', 'sudo pip install --upgrade virtualenv', 'sudo pip install bottle', 'sudo pip install --upgrade oauth2client', 'sudo pip install --upgrade google-api-python-client', 'sudo pip install beaker', 'sudo apt-get install unzip']
for n, com in enumerate(commands):
    stdin, stdout, stderr = client.exec_command(com)
    time.sleep(5)
    if n == 1:
        stdin.write('y\n')
        time.sleep(100)
    else:
        time.sleep(15)
    print "executed '"+com+"'"


if __name__=="__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Script to deploy the website')

    parser.add_argument("file", nargs=1, help='Name the zip file with the website files')

    file_name = parser.parse_args().file[0]
    scp = SCPClient(client.get_transport())
    scp.put(file_name)
    stdin, stdout, stderr = client.exec_command("unzip "+file_name)
    stdin, stdout, stderr = client.exec_command("python topera.py")
    print stdout.next()

    print "connection %s" % ("ok" if connection else "failed")
    print "key pair %s" % ("ok" if key else "failed")
    print "security group %s" % ("ok" if sec_group else "failed")
    print "reservation %s" % ("ok" if res else "failed")
    print "instance %s" % ("ok" if ins else "failed")
    print "ip %s" % ("ok" if ip else "failed")
