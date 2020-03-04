import logging
import sys, os
from paramiko import AuthenticationException
from paramiko.client import SSHClient, AutoAddPolicy
from paramiko.ssh_exception import NoValidConnectionsError
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
    def execute_some_command(self):

        try:
            command = self.config.get('ssh','command')
            stdin, stdout, stderr = self.ssh_client.exec_command(command)
            readlines = stdout.readlines()
            errlines = stderr.readlines()
            for line in readlines:
                print(line)
            for err in errlines:
                print(err)
        except Exception as e:
            logging.error(str(e))


    def multi_run_comment(self):
        if not self.shell:
            self.shell = self.ssh_client.invoke_shell()
            try:
                command_list = self.config.get('ssh', 'command_list')
                for cmd in command_list:
                    print("do cmd", cmd)
                    self.shell.send(cmd + '\n')
                    time.sleep(0.8)
                    recved_buff = self.shell.recv(1024)
                    print('recved_buff', recved_buff)
            except Exception as e:
                logging.error(str(e))


    def ssh_logout(self):
        logging.warning('will exit host')
        self.ssh_client.close()


def operate_one_machine():


    my_ssh_client = MySshClient()

    if my_ssh_client.ssh_login():
        logging.warning("login success, will execute command")

        Threads = []
        t1 = threading.Thread(target=my_ssh_client.multi_run_comment)
        t2 = threading.Thread(target=my_ssh_client.execute_some_command)
        Threads.append(t1)
        Threads.append(t2)
        for t in Threads:
            t.start()
        for t in Threads:
            t.join()
        my_ssh_client.ssh_logout()


if __name__ == '__main__':

    parser = ArgumentParser(description='参数描述')
    parser.add_argument("--verbose", help="Increase output verbosity",
                        action="store_const", const=logging.DEBUG, default=logging.INFO)
    parser.add_argument('--filename', default='config.ini')
    args = parser.parse_args()
    t3 = threading.Thread(target=operate_one_machine)
    t4 = threading.Thread(target=operate_one_machine)
    t3.start()
    t3.join()
    t4.start()
    t4.join()



