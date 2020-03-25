# -*- coding: UTF-8 -*-
import logging
import re, os, paramiko
import yaml
from paramiko import AuthenticationException
from paramiko.client import SSHClient, AutoAddPolicy
from paramiko.ssh_exception import NoValidConnectionsError
from argparse import ArgumentParser
from prometheus_client import CollectorRegistry, Gauge, pushadd_to_gateway

logging.basicConfig(
    filename='paramiko.log',
    level=logging.WARNING,
    format='%(levelname)s:%(asctime)s:%(message)s'
)



class MySshClient():
    def __init__(self, ip, target):
        self.ssh_client = SSHClient()
        self.shell = None
        self.registry = CollectorRegistry()
        self.ip = ip
        self.target = target

    def ssh_login(self):
        try:
            self.ssh_client.set_missing_host_key_policy(AutoAddPolicy())
            self.ssh_client.connect(hostname=self.ip['remote_ips']['host'], port=self.ip['remote_ips']['port'],
                                    username=self.ip['remote_ips']['username'], password=self.ip['remote_ips']['password'])

            stdin, stdout, stderr = self.ssh_client.exec_command('pwd')

            self.des = stdout.read().decode()

        except AuthenticationException:
            logging.warning('username or password error')
            return False
        except NoValidConnectionsError:
            logging.warning('connect time out')
            return False
        except:
            logging.warning('unknow error')
            return False
        return True



    def remote_scp(self):

        t = paramiko.Transport((self.ip['remote_ips']['host'], 22))

        t.connect(username=ip['remote_ips']['username'], password=ip['remote_ips']['password'])

        sftp = paramiko.SFTPClient.from_transport(t)  # sftp传输协议
        name = 'generate1.py'
        src = os.path.join(os.path.dirname(__file__), 'generate1.py').replace("\\", "/")
        self.des = self.des.strip('\r\n')
        remote_name = os.path.join(self.des, name)

        ##上传文件
        sftp.put(src, remote_name)
        t.close()


    def execute_some_command(self, command):
        try:


            stdin, stdout, stderr = self.ssh_client.exec_command(command)
            res, err = stdout.readlines(), stderr.readlines()
            result = res if res else err
            li_out = []
            tem_dict = {}
            flag = 0
            for line in result:

                if 'obdfilter' in line:
                    flag += 1
                    if flag == 1:
                        try:
                            res = re.search("((?:[0-9]{1,3}\.){3}[0-9]{1,3})", line)
                            if res:
                                server_IP = res.group(1)
                        except Exception as e:
                            logging.error(str(e))

                    if flag > 1:
                        tem_dict = {}
                        li_out.append(tem_dict)
                        store = line.split('.')[1]
                        tem_dict['store'] = store
                        res = re.search("((?:[0-9]{1,3}\.){3}[0-9]{1,3})", line)
                        if res:
                            client_IP = res.group(1)
                            tem_dict['client_IP'] = client_IP
                        store = line.split('.')[1]
                        tem_dict['store'] = store
                        tem_dict['server_IP'] = server_IP

                elif 'snapshot_time' in line:
                    snapshot_time = line.split('  ')[-1].strip('\r\n')
                    tem_dict['snapshot_time'] = snapshot_time

                elif 'read_bytes' in line:
                    read_bytes = line.split('  ')[-1].split(' ')[-1].strip('\r\n')
                    tem_dict['read_bytes'] = read_bytes

                elif 'write_bytes' in line:
                    write_bytes = line.split('  ')[-1].split(' ')[-1].strip('\r\n')
                    tem_dict['write_bytes'] = write_bytes

                else:
                    tem_dict = {}
            print(li_out)
            return li_out


        except Exception as e:
            logging.error(str(e))

    def push2gateway(self, command):

        self.read_metric = Gauge('read_push', 'status',
                                 ['server_IP', 'store_name', 'client_IP', 'snapshot_time', 'read_bytes'],
                                 registry=self.registry)

        self.write_metric = Gauge('write_push', 'status',
                                  ['server_IP', 'store_name', 'client_IP', 'snapshot_time', 'write_bytes'],
                                  registry=self.registry)

        dict_list = self.execute_some_command(command)
        try:
            for dict_tmp in dict_list:
                server_IP = dict_tmp['server_IP']
                store = dict_tmp['store']
                client_IP = dict_tmp['client_IP']
                snapshot_time = dict_tmp['snapshot_time']
                read_bytes = dict_tmp['read_bytes']
                write_bytes = dict_tmp['write_bytes']

                self.read_metric.labels(server_IP, store, client_IP, snapshot_time, read_bytes).set(read_bytes)
                self.write_metric.labels(server_IP, store, client_IP, snapshot_time, write_bytes).set(write_bytes)

            pushadd_to_gateway(self.target, job='gene_pushgateway', registry=self.registry, timeout=200)

        except Exception as e:
            logging.error(str(e))

    def ssh_logout(self):
        logging.warning('will exit host')
        self.ssh_client.close()


if __name__ == '__main__':

    parser = ArgumentParser(description='describe')
    parser.add_argument("--verbose", help="Increase output verbosity",
                        action="store_const", const=logging.DEBUG, default=logging.INFO)
    parser.add_argument('--filename', default='config.yaml')
    parser.add_argument('--command',
                        default='python generate1.py')
    args = parser.parse_args()
    filename = os.path.join(os.path.dirname(__file__), args.filename).replace("\\", "/")
    f = open(filename)
    y = yaml.load(f, Loader=yaml.FullLoader)
    target = y['pushgateway']['targets'][0]
    remoteIPs_list = y['ssh']

    command = args.command
    for ip in remoteIPs_list:

        my_ssh_client = MySshClient(ip, target)

        if my_ssh_client.ssh_login():
            logging.warning("login success, will execute command")
            my_ssh_client.remote_scp()
            my_ssh_client.push2gateway(command)
            my_ssh_client.ssh_logout()

