# -*- coding: UTF-8 -*-
import random


def structure():
    dict1 = {"server":
        [
            {"store1": [{'client1': '192.168.217.135', 'read': random.randint(100000, 10000000),
                         'write': random.randint(100000, 10000000)},
                        {'client2': '192.168.217.136', 'read': random.randint(100000, 10000000),
                         'write': random.randint(100000, 10000000)}]},

            {"store2": [{'client3': '192.168.217.137', 'read': random.randint(100000, 10000000),
                         'write': random.randint(100000, 10000000)},
                        {'client4': '192.168.217.138', 'read': random.randint(100000, 10000000),
                         'write': random.randint(100000, 10000000)}]}

        ]
    }
    print(dict1)
    return dict1


structure()
