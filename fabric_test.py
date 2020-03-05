#!/usr/bin/python
# -*- encoding: utf-8 -*-

from fabric.api import *
#定义角色，操作一致的服务器可以放在一组。因为服务器的用户端口不一样，需要在role里指定用户、IP和端口
env.roledefs = {
    'dbserver':['hairy@192.168.217.138:22'],
    'webserver':['python@192.168.217.137:22'],
}

#密码，远程服务器密码不一致时使用，格式user@host:port:pwd
env.passwords = {
    'hairy@192.168.217.138:22': '308301',
    'python@192.168.217.137:22': 'lhr308301',
}


@task                             #入口
@roles('dbserver')                #角色修饰符
@parallel                         # 并行执行
def get_memory():
    run('free -m')


@task
@roles('webserver')
@parallel
def mkfile_task():
    with cd('/home/python/'):
        run('touch log.log')

@task
def go():
    execute(get_memory)
    execute(mkfile_task)

