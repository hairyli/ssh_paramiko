import logging
import sys, os

import yaml
from paramiko import AuthenticationException
from paramiko.client import SSHClient, AutoAddPolicy
from paramiko.ssh_exception import NoValidConnectionsError
import psutil
import configparser
import time
from argparse import ArgumentParser
import threading
from prometheus_client import CollectorRegistry, Gauge, pushadd_to_gateway
import json

logging.basicConfig(
    filename='paramiko.log',
    level=logging.WARNING,
    format='%(levelname)s:%(asctime)s:%(message)s'
)


class MySshClient():
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.filename = os.path.join(os.path.dirname(__file__), args.filename).replace("\\", "/")
        self.fileyaml = os.path.join(os.path.dirname(__file__), args.fileyaml).replace("\\", "/")
        self.f = open(self.fileyaml)
        self.y = yaml.load(self.f, Loader=yaml.FullLoader)
        self.config.read(self.filename)
        self.ssh_client = SSHClient()
        self.target = self.y['pushgateway']['targets'][0]
        self.shell = None
        self.registry = CollectorRegistry()




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
            return False
        return True

    def execute_some_command(self, command):
        try:
            stdin, stdout, stderr = self.ssh_client.exec_command(command)

            res, err = stdout.read().decode(), stderr.read().decode()
            result = res if res else err
            result = eval(result)

            return result


        except Exception as e:
            logging.error(str(e))

    def push2gateway(self):

        self.g = Gauge('gene_push', 'status',
                       ['server', 'store_name', 'clentIP', 'read_bytes', 'write_bytes', 'snapshot_time'],
                       registry=self.registry)

        snapshot_time = time.time()
        result = self.execute_some_command(command)
        for dict_key in result.keys():
            server = dict_key
            store_lists = result.get(server)

        for store_dict in store_lists:
            for store in store_dict.keys():
                store = store
                for client_list in store_dict.get(store):
                    for client in client_list.keys():
                        client = client

                        read = client_list.get(client).split(',')[0]
                        write = client_list.get(client).split(',')[1]

                        self.g.labels(server, store, client, read, write, snapshot_time)

        pushadd_to_gateway(self.target, job='gene_pushgateway', registry=self.registry, timeout=200)

    def ssh_logout(self):
        logging.warning('will exit host')
        self.ssh_client.close()


if __name__ == '__main__':

    parser = ArgumentParser(description='describe')
    parser.add_argument("--verbose", help="Increase output verbosity",
                        action="store_const", const=logging.DEBUG, default=logging.INFO)
    parser.add_argument('--filename', default='config.ini')
    parser.add_argument('--fileyaml', default='pingconf.yml')
    parser.add_argument('--command', default='cd /home/python/workspace/ssh_paramiko/oss_pushgate2;python generate1.py')
    args = parser.parse_args()
    command = args.command
    my_ssh_client = MySshClient()

    if my_ssh_client.ssh_login():
        logging.warning("login success, will execute command")
        my_ssh_client.push2gateway()
