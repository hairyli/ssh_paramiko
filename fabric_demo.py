#!/usr/bin/python
# -*- encoding: utf-8 -*-
import os, sys, yaml
from fabric.api import *
from argparse import ArgumentParser
import logging

logging.basicConfig(
    filename='fabric.log',
    level=logging.INFO,
    format='%(levelname)s:%(asctime)s:%(message)s'
)


class Fabric_test():

    def __init__(self):

        self.filename = os.path.join(os.path.dirname(__file__), args.filename).replace("\\", "/")
        self.f = open(self.filename)
        self.y = yaml.load(self.f, Loader=yaml.FullLoader)
        self.roledefs = self.y['fabric']['env']['roledefs']
        self.passwords = self.y['fabric']['env']['passwords']
        self.go()

    @task                             #入口
    @roles('dbserver')                #角色修饰符
    @parallel                         # 并行执行
    def get_memory(self):

        try:
            run('free -m')
        except Exception as e:
            logging.error(e)

    @task
    @roles('webserver')
    @parallel
    def mkfile_task(self):

        try:
            with cd('/home/python/'):
                run('touch log.log')
        except Exception as e:
            logging.error(e)

    @task
    def go(self):
        execute(self.get_memory)
        execute(self.mkfile_task)




if __name__ == '__main__':
    parser = ArgumentParser(description='参数描述')
    parser.add_argument("--verbose", help="Increase output verbosity",
                        action="store_const", const=logging.DEBUG, default=logging.INFO)

    parser.add_argument('--filename', default='fabric.yaml')
    args = parser.parse_args()

    Fabric_test()






















# # 定义角色，操作一致的服务器可以放在一组。因为服务器的用户端口不一样，需要在role里指定用户、IP和端口
# env.roledefs = {
#     'dbserver': ['hairy@192.168.217.138:22'],
#     'webserver': ['python@192.168.217.137:22'],
# }
#
# # 密码，远程服务器密码不一致时使用，格式user@host:port:pwd
# env.passwords = {
#     'hairy@192.168.217.138:22': '308301',
#     'python@192.168.217.137:22': 'lhr308301',
# }