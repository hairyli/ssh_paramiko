# -*- coding: UTF-8 -*-
import time
import random
def gene():

    li = []
    for i in range(1, 2):

        clentIP = '192.168.217.' + str(i)
        snapshot_time = time.time()
        store_name = 'sxu-OST' + str(i)
        read_bytes = random.randint(100000, 10000000)
        write_bytes = random.randint(100000, 10000000)
        li.append(clentIP)
        li.append(snapshot_time)
        li.append(store_name)
        li.append(read_bytes)
        li.append(write_bytes)

    print(li)
    return li

gene()