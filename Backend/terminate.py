import boto.ec2
import boto.ec2.connection
import csv
import time
import paramiko
from scp import SCPClient

f = open('Backend/credentials.csv','r')
reader = csv.reader(f,delimiter=',')
reader.next()
key = reader.next()
f.close()
connection = boto.ec2.connect_to_region('us-east-1', aws_access_key_id=key[1], aws_secret_access_key=key[2])
# key = connection.create_key_pair('topera')
# key.save(".")

while True:
    try:
        instance_id = raw_input("Input instace ID: ")
        terminate = connection.terminate_instances(instance_ids=[instance_id])
        break
    except boto.exception.EC2ResponseError:
        print "Server returned an error, check if the ID is correct"

if terminate:
    print "Success"
else:
    print "Fail"
