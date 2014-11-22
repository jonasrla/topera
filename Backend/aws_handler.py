import boto.ec2
import boto.ec2.connection
import csv

f = open('credentials.csv','r')
reader = csv.reader(f,delimiter=',')
reader.next()
line = reader.next()
f.close()
connection = boto.ec2.connect_to_region('us-east-1', aws_access_key_id=line[1], aws_secret_access_key=line[2])
# key = connection.create_key_pair('topera')
# key.save(".")
sec_group = connection.create_security_group('csc326-group30','group for users of the search engine Topera')

connection.authorize_security_group(group_name='csc326-group30', ip_protocol='ICMP', from_port=-1, to_port=-1, cidr_ip='0.0.0.0/0')
connection.authorize_security_group(group_name='csc326-group30', ip_protocol='TCP', from_port=22, to_port=22, cidr_ip='0.0.0.0/0')
connection.authorize_security_group(group_name='csc326-group30', ip_protocol='TCP', from_port=80, to_port=80, cidr_ip='0.0.0.0/0')
res = connection.run_instances('ami-8caa1ce4', key_name="topera", security_groups=["csc326-group30"])
ins = res.instances[0]
while ins.state != unicode('running'):
    pass
ip = ins.ip_address
print ip


if __name__=="__main__":
    print "connection %s" % ("ok" if connection else "failed")
    print "key pair %s" % ("ok" if key else "failed")
    print "security group %s" % ("ok" if sec_group else "failed")
    print "reservation %s" % ("ok" if res else "failed")
    print "instance %s" % ("ok" if ins else "failed")
    print "ip %s" % ("ok" if ip else "failed")