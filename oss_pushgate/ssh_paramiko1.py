import logging
import sys, os
from paramiko import AuthenticationException
from paramiko.client import SSHClient, AutoAddPolicy
from paramiko.ssh_exception import NoValidConnectionsError
import psutil
import configparser
import time
from argparse import ArgumentParser
import threading
from prometheus_client import CollectorRegistry, Gauge, pushadd_to_gateway


logging.basicConfig(
    filename='paramiko.log',
    level=logging.WARNING,
    format='%(levelname)s:%(asctime)s:%(message)s'
)

class MySshClient():

    def __init__(self):
        self.config = configparser.ConfigParser()
        self.filename = os.path.join(os.path.dirname(__file__), args.filename).replace("\\", "/")
        self.config.read(self.filename)
        self.ssh_client = SSHClient()
        self.shell = None



    def ssh_login(self):
        try:

            self.ssh_client.set_missing_host_key_policy(AutoAddPolicy())
            self.ssh_client.connect(hostname=self.config.get('ssh', 'host'), port=self.config.get('ssh', 'port'),
                                    username=self.config.get('ssh', 'username'),
                                    password=self.config.get('ssh', 'password'))


        except AuthenticationException:
            logging.warning('username or password error')
            return False
        except NoValidConnectionsError:
            logging.warning('connect time out')
            return False
        except:
            logging.warning('unknow error')
            print("Unexpected error:", sys.exc_info()[0])
            return False
        return True


    def execute_some_command(self,command):
        try:
            stdin, stdout, stderr = self.ssh_client.exec_command(command)
            readlines = stdout.readlines()
            print(readlines)
            for line in readlines:

                print(line.strip('\n'))
                clentIP = readlines[0]
                snapshot_time = readlines[1]
                store_name = readlines[2]
                read_bytes = readlines[3]
                write_bytes = readlines[4]

            return clentIP, snapshot_time, store_name, read_bytes, write_bytes
        except Exception as e:
            logging.error(str(e))

    def push2gateway(self):

        self.registry = CollectorRegistry()

        self.g = Gauge('gene_push', 'status', ['clentIP', 'snapshot_time', 'store_name', 'read_bytes', 'write_bytes'], registry=self.registry)



        clentIP, snapshot_time, store_name, read_bytes, write_bytes = self.execute_some_command(command)

        self.g.labels(clentIP, snapshot_time, store_name, read_bytes, write_bytes)

        pushadd_to_gateway('192.168.217.137:9091', job='gene_pushgateway', registry=self.registry, timeout=200)



    def ssh_logout(self):
        logging.warning('will exit host')
        self.ssh_client.close()

if __name__ == '__main__':

    parser = ArgumentParser(description='')
    parser.add_argument("--verbose", help="Increase output verbosity",
                        action="store_const", const=logging.DEBUG, default=logging.INFO)
    parser.add_argument('--filename', default='config.ini')
    parser.add_argument('--command', default='cd /home/python/workspace/ssh_paramiko/oss_pushgate;python generate1.py')
    args = parser.parse_args()
    command = args.command
    my_ssh_client = MySshClient()

    if my_ssh_client.ssh_login():
        logging.warning("login success, will execute command")
        my_ssh_client.push2gateway()
