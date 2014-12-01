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
time.sleep(40)
print "waiting machine"
for i in range(5):
    print "Trying to connect..."
    try:
        client.connect(ip,username="ubuntu",key_filename="topera.pem", timeout=20.0)
        print "Connection Successful"
        break
    except Exception:
        time.sleep(5)
        print "Trying againg"

# channel = client.get_transport().open_session()

# commands = ['sudo apt-get install python-pip python-dev build-essential', 'sudo pip install --upgrade pip', 'sudo pip install --upgrade virtualenv', 'sudo pip install bottle', 'sudo pip install --upgrade oauth2client', 'sudo pip install --upgrade google-api-python-client', 'sudo pip install beaker']
# for com in commands:
#   channel.exec_command(com)
#   channel = client.get_transport().open_session()
#   while not channel.exit_status_ready():
#       time.sleep(1)
#       print "."
#   print "executed '"+com+"'"


# scp = SSHClient(client.get_transport())
# scp.put(file_name)


if __name__=="__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Script to deploy the website')

    parser.add_argument("file", nargs=1, help='Name the zip file with the website files')

    file_name = parser.parse_args().file[0]
    scp = SSHClient(client.get_transport())
    scp.put(file_name)
    print "connection %s" % ("ok" if connection else "failed")
    print "key pair %s" % ("ok" if key else "failed")
    print "security group %s" % ("ok" if sec_group else "failed")
    print "reservation %s" % ("ok" if res else "failed")
    print "instance %s" % ("ok" if ins else "failed")
    print "ip %s" % ("ok" if ip else "failed")
