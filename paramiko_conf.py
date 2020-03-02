import logging
import sys
from paramiko import AuthenticationException
from paramiko.client import SSHClient, AutoAddPolicy
from paramiko.ssh_exception import NoValidConnectionsError
import psutil
import configparser
import time


class MySshClient():
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read("config.ini")
        self.ssh_client = SSHClient()
        self.shell = None


    # 此函数用于输入用户名密码登录主机
    def ssh_login(self):
        try:
            # 设置允许连接known_hosts文件中的主机（默认连接不在known_hosts文件中的主机会拒绝连接抛出SSHException）
            self.ssh_client.set_missing_host_key_policy(AutoAddPolicy())
            self.ssh_client.connect(hostname=self.config.get('ssh', 'host'), port=self.config.get('ssh', 'port'),
                                    username=self.config.get('ssh', 'username'),
                                    password=self.config.get('ssh', 'password'))
            # self.ssh_client.

        except AuthenticationException:
            logging.warning('username or password error')
            return 1001
        except NoValidConnectionsError:
            logging.warning('connect time out')
            return 1002
        except:
            logging.warning('unknow error')
            print("Unexpected error:", sys.exc_info()[0])
            return 1003
        return 1000

    # 此函数用于执行command参数中的命令并打印命令执行结果
    def execute_some_command(self,command):
        stdin, stdout, stderr = self.ssh_client.exec_command(command)
        readlines = stdout.readlines()
        str1 = stdout.read().decode()
        for line in readlines:
            print(line)


    def multi_run_comment(self, command_list):
        if not self.shell:
            self.shell = self.ssh_client.invoke_shell()
            for cmd in command_list:
                print("do cmd", cmd)
                self.shell.send(cmd + '\n')
                time.sleep(0.8)
                recved_buff = self.shell.recv(1024)
                print('recved_buff', recved_buff)

    # 此函数用于退出登录
    def ssh_logout(self):
        logging.warning('will exit host')
        self.ssh_client.close()

if __name__ == '__main__':

    command_list = ['pwd', 'mkdir abc', 'cd abc', 'ls', 'touch 2.txt', 'cat 1.txt']
    my_ssh_client = MySshClient()
    if my_ssh_client.ssh_login() == 1000:
        logging.warning("{host_ip}-login success, will execute command：{command}")
        my_ssh_client.multi_run_comment(command_list)
        my_ssh_client.ssh_logout()