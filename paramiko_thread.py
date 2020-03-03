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


    # 此函数用于输入用户名密码登录主机
    def ssh_login(self):
        try:
            # 设置允许连接known_hosts文件中的主机（默认连接不在known_hosts文件中的主机会拒绝连接抛出SSHException）
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

    # 此函数用于执行command参数中的命令并打印命令执行结果
    def execute_some_command(self,command):
        try:
            stdin, stdout, stderr = self.ssh_client.exec_command(command)
            readlines = stdout.readlines()
            str1 = stdout.read().decode()
            for line in readlines:
                print(line)
        except Exception as e:
            logging.error(str(e))


    def multi_run_comment(self, command_list):
        if not self.shell:
            self.shell = self.ssh_client.invoke_shell()
            try:
                for cmd in command_list:
                    print("do cmd", cmd)
                    self.shell.send(cmd + '\n')
                    time.sleep(0.8)
                    recved_buff = self.shell.recv(1024)
                    print('recved_buff', recved_buff)
            except Exception as e:
                logging.error(str(e))

    # 此函数用于退出登录
    def ssh_logout(self):
        logging.warning('will exit host')
        self.ssh_client.close()

if __name__ == '__main__':

    parser = ArgumentParser(description='参数描述')
    parser.add_argument("--verbose", help="Increase output verbosity",
                        action="store_const", const=logging.DEBUG, default=logging.INFO)
    parser.add_argument('--filename', default='config.ini')
    parser.add_argument('--command', default='pwd')
    parser.add_argument('--nargs', nargs='+', default=['pwd', 'mkdir abc', 'ls', 'ps -ef|grep java', 'cat 1.txt'])
    args = parser.parse_args()
    command = args.command
    command_list = args.nargs
    my_ssh_client = MySshClient()

    if my_ssh_client.ssh_login():
        logging.warning("login success, will execute command")
        Threads = []
        t1 = threading.Thread(target=my_ssh_client.multi_run_comment, args=(command_list,))
        t2 = threading.Thread(target=my_ssh_client.execute_some_command, args=(command,))
        Threads.append(t1)
        Threads.append(t2)
        for t in Threads:
            t.start()
        for t in Threads:
            t.join()
        my_ssh_client.ssh_logout()
