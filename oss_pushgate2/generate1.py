# -*- coding: UTF-8 -*-


def structure():

    dict1 = {"server":
        [
            {"store1": [{'client1': 'read,write'}, {'client2': 'read,write'}]},
            {"store2": [{'client3': 'read,write'}, {'client4': 'read,write'}]}

        ]
    }
    print(dict1)
    return dict1

structure()