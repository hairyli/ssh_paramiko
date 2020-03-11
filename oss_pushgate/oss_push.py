#coding:utf-8
#!/usr/bin/python3
import os
import abc
import logging
import sys
from argparse import ArgumentParser

import yaml
import time
from prometheus_client import CollectorRegistry, Gauge, push_to_gateway, pushadd_to_gateway
import re
import requests

logging.basicConfig(
    filename='log.log',
    level=logging.INFO,
    format='%(levelname)s:%(asctime)s:%(message)s'
)


class Base_push(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def gather(self):
        raise NotImplementedError

    @abc.abstractmethod
    def processing(self):
        raise NotImplementedError


class Gene_push(Base_push):

    def __init__(self):

        self.filename = os.path.join(os.path.dirname(__file__), 'pingconf.yml').replace("\\", "/")
        self.f = open(self.filename)
        self.y = yaml.load(self.f, Loader=yaml.FullLoader)
        self.targets = self.y['pushgateway']['targets'][0]
        self.processing()

    def gather(self, ip):



        try:
            str_num = os.popen(
                'ping -c1' + ' ' + ip + '>/dev/null 2>&1;echo $?').read()
            return_num = int(str_num)
            timestamp = time.time()
            if return_num == 0:
                pingResult = os.popen('ping -c1' + ' ' + ip).read()
                res_time = re.findall(r'.*time=(\d\.?\d*) ms*', pingResult)
                if len(res_time):
                    response_time = float(res_time[0])
                status = "ok"

            if return_num == 1:
                status = "not ok"
                response_time = 0
            return ip, status, timestamp, response_time
        except Exception as e:
            logging.error(e)

    def processing(self):
        self.registry = CollectorRegistry()
        self.g = Gauge(self.type, '状态-时间', ['ip', 'status', 'timestamp', 'response_time'], registry=self.registry)

        for ip in self.ips:
            ip, status, timestamp, response_time = self.gather(ip)
            self.g.labels(ip, status, timestamp, response_time)
        try:

            pushadd_to_gateway(self.targets, job='pingIP_status', registry=self.registry, timeout=200)

        except Exception as e:
            logging.error("Failt to push:" + str(e))





if __name__ == '__main__':

    parser = ArgumentParser(description='参数描述')
    parser.add_argument("--verbose", help="Increase output verbosity",
                        action="store_const", const=logging.DEBUG, default=logging.INFO)
    parser.add_argument('--filename', default='config.ini')









