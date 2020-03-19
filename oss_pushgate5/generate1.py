# -*- coding: UTF-8 -*-
import os
import time
import random


def gene():

    with open('test.res', 'w+') as f:
        for i in range(1, 40):
            storeIP_string = "obdfilter.sxu-OST0003.exports.192.168.1.{}@tcp.stats=\r\n".format(str(i))
            snapshot_time = "snapshot_time              {}\r\n".format(time.time())
            read_bytes = "read_bytes              {}\r\n".format(random.randint(100000, 10000000))
            write_bytes = "write_bytes              {}\r\n".format(random.randint(100000, 10000000))

            f.write(storeIP_string)
            f.write(snapshot_time)
            f.write(read_bytes)
            f.write(write_bytes)


def structure():
    filename = os.path.join(os.path.dirname(__file__), 'test.res').replace("\\", "/")
    with open(filename) as file_obj:
        contents = file_obj.read()
        print(contents.rstrip())

gene()
structure()
